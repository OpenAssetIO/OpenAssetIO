// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <stdexcept>
#include <utility>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/constants.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {
// Takes a BatchElementError and throws an equivalent exception.
void throwFromBatchElementError(std::size_t index, BatchElementError error) {
  switch (error.code) {
    case BatchElementError::ErrorCode::kUnknown:
      throw UnknownBatchElementException(index, std::move(error));
    case BatchElementError::ErrorCode::kInvalidEntityReference:
      throw InvalidEntityReferenceBatchElementException(index, std::move(error));
    case BatchElementError::ErrorCode::kMalformedEntityReference:
      throw MalformedEntityReferenceBatchElementException(index, std::move(error));
    case BatchElementError::ErrorCode::kEntityAccessError:
      throw EntityAccessErrorBatchElementException(index, std::move(error));
    case BatchElementError::ErrorCode::kEntityResolutionError:
      throw EntityResolutionErrorBatchElementException(index, std::move(error));
    default:
      std::string exceptionMessage = "Invalid BatchElementError. Code: ";
      exceptionMessage += std::to_string(static_cast<int>(error.code));
      exceptionMessage += " Message: ";
      exceptionMessage += error.message;
      throw std::out_of_range{exceptionMessage};
  }
}

/**
 * Extract the entity reference prefix from a manager plugin's info
 * dictionary, if available.
 */
std::optional<Str> entityReferencePrefixFromInfo(const log::LoggerInterfacePtr &logger,
                                                 const InfoDictionary &info) {
  // Check if the info dict has the prefix key.
  if (auto iter = info.find(Str{constants::kInfoKey_EntityReferencesMatchPrefix});
      iter != info.end()) {
    if (const auto *prefixPtr = std::get_if<openassetio::Str>(&iter->second)) {
      std::string msg = "Entity reference prefix '";
      msg += *prefixPtr;
      msg +=
          "' provided by manager's info() dict. Subsequent calls to isEntityReferenceString will"
          " use this prefix rather than call the manager's implementation.";
      logger->debugApi(msg);

      return *prefixPtr;
    }

    logger->warning("Entity reference prefix given but is an invalid type: should be a string.");
  }

  // Prefix string not found, so return unset optional.
  return {};
}
}  // namespace

namespace hostApi {

ManagerPtr Manager::make(managerApi::ManagerInterfacePtr managerInterface,
                         managerApi::HostSessionPtr hostSession) {
  return std::shared_ptr<Manager>(
      new Manager(std::move(managerInterface), std::move(hostSession)));
}

Manager::Manager(managerApi::ManagerInterfacePtr managerInterface,
                 managerApi::HostSessionPtr hostSession)
    : managerInterface_{std::move(managerInterface)}, hostSession_{std::move(hostSession)} {}

Identifier Manager::identifier() const { return managerInterface_->identifier(); }

Str Manager::displayName() const { return managerInterface_->displayName(); }

InfoDictionary Manager::info() const { return managerInterface_->info(); }

StrMap Manager::updateTerminology(StrMap terms) const {
  return managerInterface_->updateTerminology(std::move(terms), hostSession_);
}

InfoDictionary Manager::settings() const { return managerInterface_->settings(hostSession_); }

void Manager::initialize(InfoDictionary managerSettings) {
  managerInterface_->initialize(std::move(managerSettings), hostSession_);

  entityReferencePrefix_ =
      entityReferencePrefixFromInfo(hostSession_->logger(), managerInterface_->info());
}

void Manager::flushCaches() { managerInterface_->flushCaches(hostSession_); }

trait::TraitsDatas Manager::managementPolicy(const trait::TraitSets &traitSets,
                                             const ContextConstPtr &context) const {
  return managerInterface_->managementPolicy(traitSets, context, hostSession_);
}

ContextPtr Manager::createContext() {
  ContextPtr context = Context::make();
  context->managerState = managerInterface_->createState(hostSession_);
  context->locale = TraitsData::make();
  return context;
}

ContextPtr Manager::createChildContext(const ContextPtr &parentContext) {
  // Copy-construct the locale so changes made to the child context don't
  // affect the parent (and visa versa).
  ContextPtr context =
      Context::make(parentContext->access, TraitsData::make(parentContext->locale));
  if (parentContext->managerState) {
    context->managerState =
        managerInterface_->createChildState(parentContext->managerState, hostSession_);
  }
  return context;
}

Str Manager::persistenceTokenForContext(const ContextPtr &context) {
  if (context->managerState) {
    return managerInterface_->persistenceTokenForState(context->managerState, hostSession_);
  }
  return "";
}

ContextPtr Manager::contextFromPersistenceToken(const Str &token) {
  ContextPtr context = Context::make();
  if (!token.empty()) {
    context->managerState = managerInterface_->stateFromPersistenceToken(token, hostSession_);
  }
  return context;
}

bool Manager::isEntityReferenceString(const Str &someString) const {
  if (!entityReferencePrefix_) {
    return managerInterface_->isEntityReferenceString(someString, hostSession_);
  }

  return someString.rfind(*entityReferencePrefix_, 0) != Str::npos;
}

const Str kCreateEntityReferenceErrorMessage = "Invalid entity reference: ";

EntityReference Manager::createEntityReference(Str entityReferenceString) const {
  if (!isEntityReferenceString(entityReferenceString)) {
    throw std::domain_error{kCreateEntityReferenceErrorMessage + entityReferenceString};
  }
  return EntityReference{std::move(entityReferenceString)};
}

std::optional<EntityReference> Manager::createEntityReferenceIfValid(
    Str entityReferenceString) const {
  if (!isEntityReferenceString(entityReferenceString)) {
    return {};
  }
  return EntityReference{std::move(entityReferenceString)};
}

void Manager::entityExists(const EntityReferences &entityReferences,
                           const ContextConstPtr &context,
                           const ExistsSuccessCallback &successCallback,
                           const BatchElementErrorCallback &errorCallback) {
  managerInterface_->entityExists(entityReferences, context, hostSession_, successCallback,
                                  errorCallback);
}

void Manager::resolve(const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
                      const ContextConstPtr &context,
                      const ResolveSuccessCallback &successCallback,
                      const BatchElementErrorCallback &errorCallback) {
  managerInterface_->resolve(entityReferences, traitSet, context, hostSession_, successCallback,
                             errorCallback);
}

// Singular Except
TraitsDataPtr hostApi::Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  TraitsDataPtr resolveResult;
  resolve(
      {entityReference}, traitSet, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [](std::size_t index, BatchElementError error) {
        throwFromBatchElementError(index, std::move(error));
      });

  return resolveResult;
}

// Singular variant
std::variant<BatchElementError, TraitsDataPtr> hostApi::Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<BatchElementError, TraitsDataPtr> resolveResult;
  resolve(
      {entityReference}, traitSet, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [&resolveResult]([[maybe_unused]] std::size_t index, BatchElementError error) {
        resolveResult = std::move(error);
      });

  return resolveResult;
}

// Multi except
std::vector<TraitsDataPtr> hostApi::Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<TraitsDataPtr> resolveResult;
  resolveResult.resize(entityReferences.size());

  resolve(
      entityReferences, traitSet, context,
      [&resolveResult](std::size_t index, TraitsDataPtr data) {
        resolveResult[index] = std::move(data);
      },
      [](std::size_t index, BatchElementError error) {
        // Implemented as if FAILFAST is true.
        throwFromBatchElementError(index, std::move(error));
      });

  return resolveResult;
}

// Multi variant
std::vector<std::variant<BatchElementError, TraitsDataPtr>> hostApi::Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<BatchElementError, TraitsDataPtr>> resolveResult;
  resolveResult.resize(entityReferences.size());
  resolve(
      entityReferences, traitSet, context,
      [&resolveResult](std::size_t index, TraitsDataPtr data) {
        resolveResult[index] = std::move(data);
      },
      [&resolveResult](std::size_t index, BatchElementError error) {
        resolveResult[index] = std::move(error);
      });

  return resolveResult;
}

void Manager::getWithRelationship(const EntityReferences &entityReferences,
                                  const TraitsDataPtr &relationshipTraitsData,
                                  const ContextConstPtr &context,
                                  const Manager::RelationshipSuccessCallback &successCallback,
                                  const Manager::BatchElementErrorCallback &errorCallback,
                                  const trait::TraitSet &resultTraitSet) {
  managerInterface_->getWithRelationship(entityReferences, relationshipTraitsData, resultTraitSet,
                                         context, hostSession_, successCallback, errorCallback);
}

void Manager::getWithRelationships(const EntityReference &entityReference,
                                   const trait::TraitsDatas &relationshipTraitsDatas,
                                   const ContextConstPtr &context,
                                   const Manager::RelationshipSuccessCallback &successCallback,
                                   const Manager::BatchElementErrorCallback &errorCallback,
                                   const trait::TraitSet &resultTraitSet) {
  managerInterface_->getWithRelationships(entityReference, relationshipTraitsDatas, resultTraitSet,
                                          context, hostSession_, successCallback, errorCallback);
}

void Manager::getWithRelationshipPaged(
    const EntityReferences &entityReferences, const TraitsDataPtr &relationshipTraitsData,
    size_t pageSize, const ContextConstPtr &context,
    const Manager::PagedRelationshipSuccessCallback &successCallback,
    const Manager::BatchElementErrorCallback &errorCallback,
    const trait::TraitSet &resultTraitSet) {
  if (pageSize == 0) {
    throw std::out_of_range{"pageSize must be greater than zero."};
  }

  /* The ManagerInterface signature provides an `EntityReferencePagerInterfacePtr`
   * in the callback type, as we don't want to force the manager to
   * construct a host type (`EntityReferencePager`), as it shouldn't
   * have any knowledge about that.
   * This callback does the converting construction and forwards through.
   */
  const auto convertingPagerSuccessCallback =
      [&hostSession = this->hostSession_, &successCallback](
          std::size_t idx, managerApi::EntityReferencePagerInterfacePtr pagerInterface) {
        auto pager = hostApi::EntityReferencePager::make(std::move(pagerInterface), hostSession);
        successCallback(idx, std::move(pager));
      };
  managerInterface_->getWithRelationshipPaged(entityReferences, relationshipTraitsData,
                                              resultTraitSet, pageSize, context, hostSession_,
                                              convertingPagerSuccessCallback, errorCallback);
}

void Manager::getWithRelationshipsPaged(
    const EntityReference &entityReference, const trait::TraitsDatas &relationshipTraitsDatas,
    size_t pageSize, const ContextConstPtr &context,
    const Manager::PagedRelationshipSuccessCallback &successCallback,
    const Manager::BatchElementErrorCallback &errorCallback,
    const trait::TraitSet &resultTraitSet) {
  if (pageSize == 0) {
    throw std::out_of_range{"pageSize must be greater than zero."};
  }

  /* The ManagerInterface signature provides an `EntityReferencePagerInterfacePtr`
   * in the callback type, as we don't want to force the manager to
   * construct a host type (`EntityReferencePager`), as it shouldn't
   * have any knowledge about that.
   * This callback does the converting construction and forwards through.
   */
  const auto convertingPagerSuccessCallback =
      [&hostSession = this->hostSession_, &successCallback](
          std::size_t idx, managerApi::EntityReferencePagerInterfacePtr pagerInterface) {
        auto pager = hostApi::EntityReferencePager::make(std::move(pagerInterface), hostSession);
        successCallback(idx, std::move(pager));
      };
  managerInterface_->getWithRelationshipsPaged(entityReference, relationshipTraitsDatas,
                                               resultTraitSet, pageSize, context, hostSession_,
                                               convertingPagerSuccessCallback, errorCallback);
}

void Manager::preflight(const EntityReferences &entityReferences,
                        const trait::TraitsDatas &traitsHints, const ContextConstPtr &context,
                        const PreflightSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  if (entityReferences.size() != traitsHints.size()) {
    std::string message = "Parameter lists must be of the same length: ";
    message += std::to_string(entityReferences.size());
    message += " entity references vs. ";
    message += std::to_string(traitsHints.size());
    message += " traits hints.";
    throw std::out_of_range{message};
  }
  managerInterface_->preflight(entityReferences, traitsHints, context, hostSession_,
                               successCallback, errorCallback);
}

EntityReference Manager::preflight(
    const EntityReference &entityReference, const TraitsDataPtr &traitsHint,
    const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result{""};
  preflight(
      {entityReference}, {traitsHint}, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [](std::size_t index, BatchElementError error) {
        throwFromBatchElementError(index, std::move(error));
      });

  return result;
}

std::variant<BatchElementError, EntityReference> Manager::preflight(
    const EntityReference &entityReference, const TraitsDataPtr &traitsHint,
    const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<BatchElementError, EntityReference> result;
  preflight(
      {entityReference}, {traitsHint}, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [&result]([[maybe_unused]] std::size_t index, BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

EntityReferences Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReferences results;
  results.resize(entityReferences.size(), EntityReference{""});

  preflight(
      entityReferences, traitsHints, context,
      [&results](std::size_t index, EntityReference preflightedRef) {
        results[index] = std::move(preflightedRef);
      },
      [](std::size_t index, BatchElementError error) {
        // Implemented as if FAILFAST is true.
        throwFromBatchElementError(index, std::move(error));
      });

  return results;
}

std::vector<std::variant<BatchElementError, EntityReference>> Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<BatchElementError, EntityReference>> results;
  results.resize(entityReferences.size());
  preflight(
      entityReferences, traitsHints, context,
      [&results](std::size_t index, EntityReference entityReference) {
        results[index] = std::move(entityReference);
      },
      [&results](std::size_t index, BatchElementError error) {
        results[index] = std::move(error);
      });

  return results;
}

void Manager::register_(const EntityReferences &entityReferences,
                        const trait::TraitsDatas &entityTraitsDatas,
                        const ContextConstPtr &context,
                        const RegisterSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  if (entityReferences.size() != entityTraitsDatas.size()) {
    std::string message = "Parameter lists must be of the same length: ";
    message += std::to_string(entityReferences.size());
    message += " entity references vs. ";
    message += std::to_string(entityTraitsDatas.size());
    message += " traits datas.";
    throw std::out_of_range{message};
  }
  return managerInterface_->register_(entityReferences, entityTraitsDatas, context, hostSession_,
                                      successCallback, errorCallback);
}

// Singular Except
EntityReference hostApi::Manager::register_(
    const EntityReference &entityReference, const TraitsDataPtr &entityTraitsData,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result("");
  register_(
      {entityReference}, {entityTraitsData}, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [](std::size_t index, BatchElementError error) {
        throwFromBatchElementError(index, std::move(error));
      });

  return result;
}

// Singular variant
std::variant<BatchElementError, EntityReference> hostApi::Manager::register_(
    const EntityReference &entityReference, const TraitsDataPtr &entityTraitsData,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<BatchElementError, EntityReference> result;
  register_(
      {entityReference}, {entityTraitsData}, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [&result]([[maybe_unused]] std::size_t index, BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<EntityReference> hostApi::Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<EntityReference> result;
  result.resize(entityReferences.size(), EntityReference{""});

  register_(
      entityReferences, entityTraitsDatas, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        result[index] = std::move(registeredRef);
      },
      [](std::size_t index, BatchElementError error) {
        // Implemented as if FAILFAST is true.
        throwFromBatchElementError(index, std::move(error));
      });

  return result;
}

// Multi variant
std::vector<std::variant<BatchElementError, EntityReference>> hostApi::Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<BatchElementError, EntityReference>> result;
  result.resize(entityReferences.size());
  register_(
      entityReferences, entityTraitsDatas, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        result[index] = std::move(registeredRef);
      },
      [&result](std::size_t index, BatchElementError error) { result[index] = std::move(error); });

  return result;
}

managerApi::ManagerInterfacePtr Manager::_interface() const { return managerInterface_; }
managerApi::HostSessionPtr Manager::_hostSession() const { return hostSession_; }

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
