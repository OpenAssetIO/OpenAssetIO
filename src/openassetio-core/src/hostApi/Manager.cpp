// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {
// Takes a BatchElementError and throws an equivalent exception.
void throwFromBatchElementError(std::size_t index, const BatchElementError &error) {
  switch (error.code) {
    case BatchElementError::ErrorCode::kUnknown:
      throw UnknownBatchElementException(index, error);
    case BatchElementError::ErrorCode::kInvalidEntityReference:
      throw InvalidEntityReferenceBatchElementException(index, error);
    case BatchElementError::ErrorCode::kMalformedEntityReference:
      throw MalformedEntityReferenceBatchElementException(index, error);
    case BatchElementError::ErrorCode::kEntityAccessError:
      throw EntityAccessErrorBatchElementException(index, error);
    case BatchElementError::ErrorCode::kEntityResolutionError:
      throw EntityResolutionErrorBatchElementException(index, error);
    default:
      std::string exceptionMessage = "Invalid BatchElementError. Code: ";
      exceptionMessage += std::to_string(static_cast<int>(error.code));
      exceptionMessage += " Message: ";
      exceptionMessage += error.message;
      throw std::out_of_range{exceptionMessage};
  }
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

InfoDictionary Manager::settings() const { return managerInterface_->settings(hostSession_); }

void Manager::initialize(InfoDictionary managerSettings) {
  managerInterface_->initialize(std::move(managerSettings), hostSession_);
}

trait::TraitsDatas Manager::managementPolicy(const trait::TraitSets &traitSets,
                                             const ContextConstPtr &context) const {
  return managerInterface_->managementPolicy(traitSets, context, hostSession_);
}

ContextPtr Manager::createContext() {
  ContextPtr context = Context::make();
  context->managerState = managerInterface_->createState(hostSession_);
  return context;
}

ContextPtr Manager::createChildContext(const ContextPtr &parentContext) {
  ContextPtr context =
      Context::make(parentContext->access, parentContext->retention, parentContext->locale);
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
  return managerInterface_->isEntityReferenceString(someString, hostSession_);
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
      [&resolveResult]([[maybe_unused]] std::size_t index, const TraitsDataPtr &data) {
        resolveResult = data;
      },
      [](std::size_t index, const BatchElementError &error) {
        throwFromBatchElementError(index, error);
      });

  return resolveResult;
}

// Singular variant
std::variant<TraitsDataPtr, BatchElementError> hostApi::Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<TraitsDataPtr, BatchElementError> resolveResult;
  resolve(
      {entityReference}, traitSet, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, const TraitsDataPtr &data) {
        resolveResult = data;
      },
      [&resolveResult]([[maybe_unused]] std::size_t index, const BatchElementError &error) {
        resolveResult = error;
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
      [&resolveResult](std::size_t index, const TraitsDataPtr &data) {
        resolveResult[index] = data;
      },
      [](std::size_t index, const BatchElementError &error) {
        // Implemented as if FAILFAST is true.
        throwFromBatchElementError(index, error);
      });

  return resolveResult;
}

// Multi variant
std::vector<std::variant<TraitsDataPtr, BatchElementError>> hostApi::Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<TraitsDataPtr, BatchElementError>> resolveResult;
  resolveResult.resize(entityReferences.size());
  resolve(
      entityReferences, traitSet, context,
      [&resolveResult](std::size_t index, const TraitsDataPtr &data) {
        resolveResult[index] = data;
      },
      [&resolveResult](std::size_t index, const BatchElementError &error) {
        resolveResult[index] = error;
      });

  return resolveResult;
}

void Manager::preflight(const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
                        const ContextConstPtr &context,
                        const PreflightSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  managerInterface_->preflight(entityReferences, traitSet, context, hostSession_, successCallback,
                               errorCallback);
}

void Manager::register_(const EntityReferences &entityReferences,
                        const trait::TraitsDatas &entityTraitsDatas,
                        const ContextConstPtr &context,
                        const RegisterSuccessCallback &successCallback,
                        const BatchElementErrorCallback &errorCallback) {
  if (entityReferences.size() != entityTraitsDatas.size()) {
    throw std::out_of_range{"Parameter lists must be of the same length"};
  }

  if (!entityTraitsDatas.empty()) {
    const trait::TraitSet firstTraitSet = entityTraitsDatas[0]->traitSet();
    for (std::size_t idx = 1; idx < entityTraitsDatas.size(); ++idx) {
      const trait::TraitSet currentTraitSet = entityTraitsDatas[idx]->traitSet();
      if (currentTraitSet != firstTraitSet) {
        Str msg = "Mismatched traits at index ";
        msg += std::to_string(idx);
        // TODO(DF): expand on error message to include actual trait
        //  set.
        throw std::invalid_argument{msg};
      }
    }
  }

  return managerInterface_->register_(entityReferences, entityTraitsDatas, context, hostSession_,
                                      successCallback, errorCallback);
}

managerApi::ManagerInterfacePtr Manager::_interface() const { return managerInterface_; }
managerApi::HostSessionPtr Manager::_hostSession() const { return hostSession_; }
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
