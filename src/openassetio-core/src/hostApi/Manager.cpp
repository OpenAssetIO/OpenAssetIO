// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <array>
#include <cstddef>
#include <memory>
#include <optional>
#include <string>
#include <utility>
#include <variant>
#include <vector>

#include <fmt/core.h>
#include <fmt/format.h>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/access.hpp>
#include <openassetio/constants.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {

/**
 * Validate the supplied ManagerInterface supports all required
 * capabilities, or throw a ConfigurationException.
 *
 * These capabilities are required at runtime, but not enforced at
 * compile time, as multi-language implementations may only provide the
 * implementation in one of the component languages.
 */
void verifyRequiredCapabilities(const managerApi::ManagerInterfacePtr &interface) {
  using managerApi::ManagerInterface;

  static constexpr std::array kRequiredCapabilities = {
      ManagerInterface::Capability::kEntityReferenceIdentification,
      ManagerInterface::Capability::kManagementPolicyQueries,
      ManagerInterface::Capability::kEntityTraitIntrospection,
  };

  std::vector<std::string> missingCapabilities;
  for (const ManagerInterface::Capability capability : kRequiredCapabilities) {
    if (!interface->hasCapability(capability)) {
      missingCapabilities.emplace_back(
          ManagerInterface::kCapabilityNames[static_cast<std::size_t>(capability)]);
    }
  }

  if (missingCapabilities.empty()) {
    return;
  }

  const std::string msg =
      format("Manager implementation for '{}' does not support the required capabilities: {}",
             interface->identifier(), fmt::join(missingCapabilities, ", "));

  throw errors::ConfigurationException(msg);
}

/**
 * Extract the entity reference prefix from a manager plugin's info
 * dictionary, if available.
 */
std::optional<Str> entityReferencePrefixFromInfo(const log::LoggerInterfacePtr &logger,
                                                 const InfoDictionary &info) {
  // Check if the info dict has the prefix key.
  if (const auto iter = info.find(Str{constants::kInfoKey_EntityReferencesMatchPrefix});
      iter != info.end()) {
    if (const auto *prefixPtr = std::get_if<Str>(&iter->second)) {
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

bool Manager::hasCapability(Capability capability) {
  return managerInterface_->hasCapability(
      static_cast<managerApi::ManagerInterface::Capability>(capability));
}

InfoDictionary Manager::info() { return managerInterface_->info(); }

StrMap Manager::updateTerminology(StrMap terms) {
  return managerInterface_->updateTerminology(std::move(terms), hostSession_);
}

InfoDictionary Manager::settings() { return managerInterface_->settings(hostSession_); }

void Manager::initialize(InfoDictionary managerSettings) {
  managerInterface_->initialize(std::move(managerSettings), hostSession_);

  // Verify the manager has required capabilities. This must only be
  // done after initialization, to ensure we can support proxy interface
  // implementations that need initializing to configure the proxied
  // implementation
  verifyRequiredCapabilities(managerInterface_);

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
  if (hasCapability(Capability::kStatefulContexts)) {
    context->managerState = managerInterface_->createState(hostSession_);
  }
  context->locale = trait::TraitsData::make();
  return context;
}

ContextPtr Manager::createChildContext(const ContextPtr &parentContext) {
  // Copy-construct the locale so changes made to the child context
  // don't affect the parent (and vice versa).
  ContextPtr context = Context::make(trait::TraitsData::make(parentContext->locale));
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

void Manager::entityTraits(const EntityReferences &entityReferences,
                           const access::EntityTraitsAccess entityTraitsAccess,
                           const ContextConstPtr &context,
                           const EntityTraitsSuccessCallback &successCallback,
                           const BatchElementErrorCallback &errorCallback) {
  managerInterface_->entityTraits(entityReferences, entityTraitsAccess, context, hostSession_,
                                  successCallback, errorCallback);
}

void Manager::resolve(const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
                      const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
                      const ResolveSuccessCallback &successCallback,
                      const BatchElementErrorCallback &errorCallback) {
  managerInterface_->resolve(entityReferences, traitSet, resolveAccess, context, hostSession_,
                             successCallback, errorCallback);
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
                                  const trait::TraitsDataPtr &relationshipTraitsData,
                                  size_t pageSize, const access::RelationsAccess relationsAccess,
                                  const ContextConstPtr &context,
                                  const RelationshipQuerySuccessCallback &successCallback,
                                  const BatchElementErrorCallback &errorCallback,
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
  managerInterface_->getWithRelationship(entityReferences, relationshipTraitsData, resultTraitSet,
                                         pageSize, relationsAccess, context, hostSession_,
                                         convertingPagerSuccessCallback, errorCallback);
}

void Manager::getWithRelationships(
    const EntityReference &entityReference, const trait::TraitsDatas &relationshipTraitsDatas,
    size_t pageSize, const access::RelationsAccess relationsAccess, const ContextConstPtr &context,
    const Manager::RelationshipQuerySuccessCallback &successCallback,
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
  managerInterface_->getWithRelationships(entityReference, relationshipTraitsDatas, resultTraitSet,
                                          pageSize, relationsAccess, context, hostSession_,
                                          convertingPagerSuccessCallback, errorCallback);
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
  managerInterface_->register_(entityReferences, entityTraitsDatas, publishingAccess, context,
                               hostSession_, successCallback, errorCallback);
}

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
