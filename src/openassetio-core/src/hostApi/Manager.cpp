// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <stdexcept>
#include <utility>

#include <fmt/format.h>

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

#include "../errors/exceptionMessages.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {
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
      logger->debugApi(
          fmt::format("Entity reference prefix '{}' provided by manager's info() dict. Subsequent"
                      " calls to isEntityReferenceString will use this prefix rather than call the"
                      " manager's implementation.",
                      *prefixPtr));

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

InfoDictionary Manager::info() { return managerInterface_->info(); }

StrMap Manager::updateTerminology(StrMap terms) {
  return managerInterface_->updateTerminology(std::move(terms), hostSession_);
}

InfoDictionary Manager::settings() { return managerInterface_->settings(hostSession_); }

void Manager::initialize(InfoDictionary managerSettings) {
  managerInterface_->initialize(std::move(managerSettings), hostSession_);

  entityReferencePrefix_ =
      entityReferencePrefixFromInfo(hostSession_->logger(), managerInterface_->info());
}

void Manager::flushCaches() { managerInterface_->flushCaches(hostSession_); }

trait::TraitsDatas Manager::managementPolicy(const trait::TraitSets &traitSets,
                                             const access::PolicyAccess policyAccess,
                                             const ContextConstPtr &context) {
  return managerInterface_->managementPolicy(traitSets, policyAccess, context, hostSession_);
}

ContextPtr Manager::createContext() {
  ContextPtr context = Context::make();
  context->managerState = managerInterface_->createState(hostSession_);
  context->locale = TraitsData::make();
  return context;
}

ContextPtr Manager::createChildContext(const ContextPtr &parentContext) {
  // Copy-construct the locale so changes made to the child context
  // don't affect the parent (and vice versa).
  ContextPtr context = Context::make(TraitsData::make(parentContext->locale));
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

bool Manager::isEntityReferenceString(const Str &someString) {
  if (!entityReferencePrefix_) {
    return managerInterface_->isEntityReferenceString(someString, hostSession_);
  }

  return someString.rfind(*entityReferencePrefix_, 0) != Str::npos;
}

const Str kCreateEntityReferenceErrorMessage = "Invalid entity reference: ";

EntityReference Manager::createEntityReference(Str entityReferenceString) {
  if (!isEntityReferenceString(entityReferenceString)) {
    throw errors::InputValidationException{kCreateEntityReferenceErrorMessage +
                                           entityReferenceString};
  }
  return EntityReference{std::move(entityReferenceString)};
}

std::optional<EntityReference> Manager::createEntityReferenceIfValid(Str entityReferenceString) {
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
                      const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
                      const ResolveSuccessCallback &successCallback,
                      const BatchElementErrorCallback &errorCallback) {
  managerInterface_->resolve(entityReferences, traitSet, resolveAccess, context, hostSession_,
                             successCallback, errorCallback);
}

// Singular Except
TraitsDataPtr hostApi::Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  TraitsDataPtr resolveResult;
  resolve(
      {entityReference}, traitSet, resolveAccess, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [&entityReference, resolveAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReference, static_cast<access::Access>(resolveAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return resolveResult;
}

// Singular variant
std::variant<errors::BatchElementError, TraitsDataPtr> hostApi::Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, TraitsDataPtr> resolveResult;
  resolve(
      {entityReference}, traitSet, resolveAccess, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [&resolveResult]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        resolveResult = std::move(error);
      });

  return resolveResult;
}

// Multi except
std::vector<TraitsDataPtr> hostApi::Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<TraitsDataPtr> resolveResult;
  resolveResult.resize(entityReferences.size());

  resolve(
      entityReferences, traitSet, resolveAccess, context,
      [&resolveResult](std::size_t index, TraitsDataPtr data) {
        resolveResult[index] = std::move(data);
      },
      [&entityReferences, resolveAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReferences[index], static_cast<access::Access>(resolveAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return resolveResult;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, TraitsDataPtr>> hostApi::Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, TraitsDataPtr>> resolveResult;
  resolveResult.resize(entityReferences.size());
  resolve(
      entityReferences, traitSet, resolveAccess, context,
      [&resolveResult](std::size_t index, TraitsDataPtr data) {
        resolveResult[index] = std::move(data);
      },
      [&resolveResult](std::size_t index, errors::BatchElementError error) {
        resolveResult[index] = std::move(error);
      });

  return resolveResult;
}

void Manager::defaultEntityReference(const trait::TraitSets &traitSets,
                                     const access::DefaultEntityAccess defaultEntityAccess,
                                     const ContextConstPtr &context,
                                     const DefaultEntityReferenceSuccessCallback &successCallback,
                                     const BatchElementErrorCallback &errorCallback) {
  managerInterface_->defaultEntityReference(traitSets, defaultEntityAccess, context, hostSession_,
                                            successCallback, errorCallback);
}

void Manager::getWithRelationship(const EntityReferences &entityReferences,
                                  const TraitsDataPtr &relationshipTraitsData,
                                  const access::RelationsAccess relationsAccess,
                                  const ContextConstPtr &context,
                                  const Manager::RelationshipSuccessCallback &successCallback,
                                  const Manager::BatchElementErrorCallback &errorCallback,
                                  const trait::TraitSet &resultTraitSet) {
  managerInterface_->getWithRelationship(entityReferences, relationshipTraitsData, resultTraitSet,
                                         relationsAccess, context, hostSession_, successCallback,
                                         errorCallback);
}

void Manager::getWithRelationships(const EntityReference &entityReference,
                                   const trait::TraitsDatas &relationshipTraitsDatas,
                                   const access::RelationsAccess relationsAccess,
                                   const ContextConstPtr &context,
                                   const Manager::RelationshipSuccessCallback &successCallback,
                                   const Manager::BatchElementErrorCallback &errorCallback,
                                   const trait::TraitSet &resultTraitSet) {
  managerInterface_->getWithRelationships(entityReference, relationshipTraitsDatas, resultTraitSet,
                                          relationsAccess, context, hostSession_, successCallback,
                                          errorCallback);
}

void Manager::getWithRelationshipPaged(
    const EntityReferences &entityReferences, const TraitsDataPtr &relationshipTraitsData,
    size_t pageSize, const access::RelationsAccess relationsAccess, const ContextConstPtr &context,
    const Manager::PagedRelationshipSuccessCallback &successCallback,
    const Manager::BatchElementErrorCallback &errorCallback,
    const trait::TraitSet &resultTraitSet) {
  if (pageSize == 0) {
    throw errors::InputValidationException{"pageSize must be greater than zero."};
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
  managerInterface_->getWithRelationshipPaged(
      entityReferences, relationshipTraitsData, resultTraitSet, pageSize, relationsAccess, context,
      hostSession_, convertingPagerSuccessCallback, errorCallback);
}

void Manager::getWithRelationshipsPaged(
    const EntityReference &entityReference, const trait::TraitsDatas &relationshipTraitsDatas,
    size_t pageSize, const access::RelationsAccess relationsAccess, const ContextConstPtr &context,
    const Manager::PagedRelationshipSuccessCallback &successCallback,
    const Manager::BatchElementErrorCallback &errorCallback,
    const trait::TraitSet &resultTraitSet) {
  if (pageSize == 0) {
    throw errors::InputValidationException{"pageSize must be greater than zero."};
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
  managerInterface_->getWithRelationshipsPaged(
      entityReference, relationshipTraitsDatas, resultTraitSet, pageSize, relationsAccess, context,
      hostSession_, convertingPagerSuccessCallback, errorCallback);
}

void Manager::preflight(const EntityReferences &entityReferences,
                        const trait::TraitsDatas &traitsHints,
                        const access::PublishingAccess publishingAccess,
                        const ContextConstPtr &context,
                        const PreflightSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  if (entityReferences.size() != traitsHints.size()) {
    std::string message = "Parameter lists must be of the same length: ";
    message += std::to_string(entityReferences.size());
    message += " entity references vs. ";
    message += std::to_string(traitsHints.size());
    message += " traits hints.";
    throw errors::InputValidationException{message};
  }
  managerInterface_->preflight(entityReferences, traitsHints, publishingAccess, context,
                               hostSession_, successCallback, errorCallback);
}

EntityReference Manager::preflight(
    const EntityReference &entityReference, const TraitsDataPtr &traitsHint,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result{""};
  preflight(
      {entityReference}, {traitsHint}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [&entityReference, publishingAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReference, static_cast<access::Access>(publishingAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

std::variant<errors::BatchElementError, EntityReference> Manager::preflight(
    const EntityReference &entityReference, const TraitsDataPtr &traitsHint,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, EntityReference> result;
  preflight(
      {entityReference}, {traitsHint}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

EntityReferences Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReferences results;
  results.resize(entityReferences.size(), EntityReference{""});

  preflight(
      entityReferences, traitsHints, publishingAccess, context,
      [&results](std::size_t index, EntityReference preflightedRef) {
        results[index] = std::move(preflightedRef);
      },
      [&entityReferences, publishingAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReferences[index], static_cast<access::Access>(publishingAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return results;
}

std::vector<std::variant<errors::BatchElementError, EntityReference>> Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReference>> results;
  results.resize(entityReferences.size());
  preflight(
      entityReferences, traitsHints, publishingAccess, context,
      [&results](std::size_t index, EntityReference entityReference) {
        results[index] = std::move(entityReference);
      },
      [&results](std::size_t index, errors::BatchElementError error) {
        results[index] = std::move(error);
      });

  return results;
}

void Manager::register_(const EntityReferences &entityReferences,
                        const trait::TraitsDatas &entityTraitsDatas,
                        const access::PublishingAccess publishingAccess,
                        const ContextConstPtr &context,
                        const RegisterSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  if (entityReferences.size() != entityTraitsDatas.size()) {
    std::string message = "Parameter lists must be of the same length: ";
    message += std::to_string(entityReferences.size());
    message += " entity references vs. ";
    message += std::to_string(entityTraitsDatas.size());
    message += " traits datas.";
    throw errors::InputValidationException{message};
  }
  return managerInterface_->register_(entityReferences, entityTraitsDatas, publishingAccess,
                                      context, hostSession_, successCallback, errorCallback);
}

// Singular Except
EntityReference hostApi::Manager::register_(
    const EntityReference &entityReference, const TraitsDataPtr &entityTraitsData,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result("");
  register_(
      {entityReference}, {entityTraitsData}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [&entityReference, publishingAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReference, static_cast<access::Access>(publishingAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Singular variant
std::variant<errors::BatchElementError, EntityReference> hostApi::Manager::register_(
    const EntityReference &entityReference, const TraitsDataPtr &entityTraitsData,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, EntityReference> result;
  register_(
      {entityReference}, {entityTraitsData}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<EntityReference> hostApi::Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<EntityReference> result;
  result.resize(entityReferences.size(), EntityReference{""});

  register_(
      entityReferences, entityTraitsDatas, publishingAccess, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        result[index] = std::move(registeredRef);
      },
      [&entityReferences, publishingAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, entityReferences[index], static_cast<access::Access>(publishingAccess));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, EntityReference>> hostApi::Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReference>> result;
  result.resize(entityReferences.size());
  register_(
      entityReferences, entityTraitsDatas, publishingAccess, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        result[index] = std::move(registeredRef);
      },
      [&result](std::size_t index, errors::BatchElementError error) {
        result[index] = std::move(error);
      });

  return result;
}

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
