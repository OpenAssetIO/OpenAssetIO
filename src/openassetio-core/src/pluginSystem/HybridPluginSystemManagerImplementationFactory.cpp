// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <algorithm>
#include <cassert>
#include <memory>

#include <fmt/format.h>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/HybridPluginSystemManagerImplementationFactory.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

namespace {

/**
 * A ManagerInterface implementation that composes multiple child
 * ManagerInterfaces and forwards API calls to one of the children.
 *
 * For most API methods, the call is forwarded to the first child that
 * satisfies the required capability for that API call, or calls the
 * base class implementation if no child satisfies the required
 * capability. The priority order of children is defined by the order
 * that they were provided to the constructor.
 *
 * For API calls that have no associated capability, either the first
 * child is chosen, or the results from all children are merged - see
 * method-specific docs for details.
 */
class HybridManagerInterface : public managerApi::ManagerInterface {
  using ManagerInterfaces = std::vector<managerApi::ManagerInterfacePtr>;

 public:
  explicit HybridManagerInterface(ManagerInterfaces managerInterfacess)
      : managerInterfaces_{std::move(managerInterfacess)} {
    // Precondition.
    // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
    assert(!managerInterfaces_.empty());
  }

  /**
   * Return the identifier of the first child, on the understanding that
   * all child implementations have the same identifier.
   */
  [[nodiscard]] Identifier identifier() const override {
    return managerInterfaces_.front()->identifier();
  }

  /**
   * Return the name of the first child, on the assumption that all
   * child implementations have the same name.
   */
  [[nodiscard]] Str displayName() const override {
    return managerInterfaces_.front()->displayName();
  }

  /**
   * Merge the results of `info()` from all child implementations, with
   * the first implementation taking precedence in case of a conflict.
   */
  [[nodiscard]] InfoDictionary info() override {
    InfoDictionary result;
    for (const auto& managerInterface : managerInterfaces_) {
      result.merge(managerInterface->info());
    }
    return result;
  }

  /**
   * Merge the results of `settings()` from all child implementations,
   * with the first implementation taking precedence in case of a
   * conflict.
   */
  [[nodiscard]] InfoDictionary settings(const managerApi::HostSessionPtr& hostSession) override {
    InfoDictionary result;
    for (const auto& managerInterface : managerInterfaces_) {
      result.merge(managerInterface->settings(hostSession));
    }
    return result;
  }

  /**
   * This hybrid manager has a capability if at least one of its child
   * implementations has the capability.
   */
  [[nodiscard]] bool hasCapability(const Capability capability) override {
    return managerInterfacesByCapability_.count(capability) > 0;
  }

  /**
   * All child implementations are initialized with the all the same
   * settings.
   *
   * Once initialization of child implementations is complete, a mapping
   * of capability to implementation is constructed, which will be used
   * to dispatch to the appropriate implementation in subsequent API
   * methods.
   */
  void initialize(InfoDictionary managerSettings,
                  const managerApi::HostSessionPtr& hostSession) override {
    for (const auto& managerInterface : managerInterfaces_) {
      managerInterface->initialize(managerSettings, hostSession);
    }
    // Cache a mapping of the first child interface that supports each
    // capability.
    //
    // Caching now avoids the need to call hasCapability() on
    // the child implementations again (and repeatedly) in the API
    // methods, which could be expensive if, for example, a network call
    // is required, or we are calling out to Python and locking the
    // GIL, etc. The disadvantage is that capabilities cannot change
    // after plugins have been loaded.
    managerInterfacesByCapability_.reserve(kCapabilityNames.size());
    for (std::size_t capabilityIdx = 0; capabilityIdx < kCapabilityNames.size(); ++capabilityIdx) {
      const auto capability = static_cast<Capability>(capabilityIdx);
      for (const auto& managerInterface : managerInterfaces_) {
        if (managerInterface->hasCapability(capability)) {
          managerInterfacesByCapability_[capability] = managerInterface;
          break;
        }
      }
    }
  }

  /**
   * All child implementations flushed.
   */
  void flushCaches(const managerApi::HostSessionPtr& hostSession) override {
    for (const auto& managerInterface : managerInterfaces_) {
      managerInterface->flushCaches(hostSession);
    }
  }

  /*
   * The remaining API methods all dispatch to the first child that
   * has the capability, or to the base class implementation if no child
   * has the capability.
   */

  /**
   * Convenience macro to call a method on the appropriate child manager
   * for a capability, or else call the base class implementation.
   */
#define INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(capability, method, ...)                        \
  [&] {                                                                                     \
    if (const auto& capabilityAndManager = managerInterfacesByCapability_.find(capability); \
        capabilityAndManager != cend(managerInterfacesByCapability_)) {                     \
      return capabilityAndManager->second->method(__VA_ARGS__);                             \
    }                                                                                       \
    return ManagerInterface::method(__VA_ARGS__);                                           \
  }()

  [[nodiscard]] StrMap updateTerminology(StrMap terms,
                                         const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kCustomTerminology, updateTerminology,
                                               std::move(terms), hostSession);
  }

  [[nodiscard]] trait::TraitsDatas managementPolicy(
      const trait::TraitSets& traitSets, access::PolicyAccess policyAccess,
      const ContextConstPtr& context, const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kManagementPolicyQueries,
                                               managementPolicy, traitSets, policyAccess, context,
                                               hostSession);
  }

  [[nodiscard]] managerApi::ManagerStateBasePtr createState(
      const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kStatefulContexts, createState,
                                               hostSession);
  }

  [[nodiscard]] managerApi::ManagerStateBasePtr createChildState(
      const managerApi::ManagerStateBasePtr& parentState,
      const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kStatefulContexts, createChildState,
                                               parentState, hostSession);
  }

  [[nodiscard]] Str persistenceTokenForState(
      const managerApi::ManagerStateBasePtr& state,
      const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kStatefulContexts,
                                               persistenceTokenForState, state, hostSession);
  }

  [[nodiscard]] managerApi::ManagerStateBasePtr stateFromPersistenceToken(
      const Str& token, const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kStatefulContexts,
                                               stateFromPersistenceToken, token, hostSession);
  }

  [[nodiscard]] bool isEntityReferenceString(
      const Str& someString, const managerApi::HostSessionPtr& hostSession) override {
    return INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kEntityReferenceIdentification,
                                               isEntityReferenceString, someString, hostSession);
  }

  void entityExists(const EntityReferences& entityReferences, const ContextConstPtr& context,
                    const managerApi::HostSessionPtr& hostSession,
                    const ExistsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kExistenceQueries, entityExists,
                                        entityReferences, context, hostSession, successCallback,
                                        errorCallback);
  }

  void entityTraits(const EntityReferences& entityReferences,
                    access::EntityTraitsAccess entityTraitsAccess, const ContextConstPtr& context,
                    const managerApi::HostSessionPtr& hostSession,
                    const EntityTraitsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kEntityTraitIntrospection, entityTraits,
                                        entityReferences, entityTraitsAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               access::ResolveAccess resolveAccess, const ContextConstPtr& context,
               const managerApi::HostSessionPtr& hostSession,
               const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kResolution, resolve, entityReferences,
                                        traitSet, resolveAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

  void defaultEntityReference(const trait::TraitSets& traitSets,
                              access::DefaultEntityAccess defaultEntityAccess,
                              const ContextConstPtr& context,
                              const managerApi::HostSessionPtr& hostSession,
                              const DefaultEntityReferenceSuccessCallback& successCallback,
                              const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kDefaultEntityReferences,
                                        defaultEntityReference, traitSets, defaultEntityAccess,
                                        context, hostSession, successCallback, errorCallback);
  }

  void getWithRelationship(const EntityReferences& entityReferences,
                           const trait::TraitsDataPtr& relationshipTraitsData,
                           const trait::TraitSet& resultTraitSet, size_t pageSize,
                           access::RelationsAccess relationsAccess, const ContextConstPtr& context,
                           const managerApi::HostSessionPtr& hostSession,
                           const RelationshipQuerySuccessCallback& successCallback,
                           const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kRelationshipQueries, getWithRelationship,
                                        entityReferences, relationshipTraitsData, resultTraitSet,
                                        pageSize, relationsAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

  void getWithRelationships(const EntityReference& entityReference,
                            const trait::TraitsDatas& relationshipTraitsDatas,
                            const trait::TraitSet& resultTraitSet, size_t pageSize,
                            access::RelationsAccess relationsAccess,
                            const ContextConstPtr& context,
                            const managerApi::HostSessionPtr& hostSession,
                            const RelationshipQuerySuccessCallback& successCallback,
                            const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kRelationshipQueries, getWithRelationships,
                                        entityReference, relationshipTraitsDatas, resultTraitSet,
                                        pageSize, relationsAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

  void preflight(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsHints,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const managerApi::HostSessionPtr& hostSession,
                 const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kPublishing, preflight, entityReferences,
                                        traitsHints, publishingAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

  void register_(const EntityReferences& entityReferences,
                 const trait::TraitsDatas& entityTraitsDatas,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const managerApi::HostSessionPtr& hostSession,
                 const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    INVOKE_CAPABLE_MANAGER_FOR_FUNCTION(Capability::kPublishing, register_, entityReferences,
                                        entityTraitsDatas, publishingAccess, context, hostSession,
                                        successCallback, errorCallback);
  }

 private:
  ManagerInterfaces managerInterfaces_;
  std::unordered_map<Capability, managerApi::ManagerInterfacePtr> managerInterfacesByCapability_;
};
}  // namespace

HybridPluginSystemManagerImplementationFactoryPtr
HybridPluginSystemManagerImplementationFactory::make(
    ManagerImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger) {
  if (factories.empty()) {
    throw errors::InputValidationException{
        "HybridPluginSystem: At least one child manager implementation factory must be provided"};
  }

  return std::make_shared<HybridPluginSystemManagerImplementationFactory>(
      HybridPluginSystemManagerImplementationFactory{std::move(factories), std::move(logger)});
}

HybridPluginSystemManagerImplementationFactory::HybridPluginSystemManagerImplementationFactory(
    ManagerImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger)
    : ManagerImplementationFactoryInterface{std::move(logger)}, factories_{std::move(factories)} {}

Identifiers HybridPluginSystemManagerImplementationFactory::identifiers() {
  Identifiers identifiers;
  // Collect all identifiers from all factories.
  for (const auto& factory : factories_) {
    Identifiers factoryIdentifiers = factory->identifiers();
    identifiers.insert(end(identifiers), make_move_iterator(begin(factoryIdentifiers)),
                       make_move_iterator(end(factoryIdentifiers)));
  }
  // Sort and remove duplicates.
  sort(begin(identifiers), end(identifiers));
  identifiers.erase(unique(begin(identifiers), end(identifiers)), end(identifiers));
  return identifiers;
}

managerApi::ManagerInterfacePtr HybridPluginSystemManagerImplementationFactory::instantiate(
    const Identifier& identifier) {
  std::vector<managerApi::ManagerInterfacePtr> managerInterfaces;

  for (const auto& factory : factories_) {
    const Identifiers& factoryIdentifiers = factory->identifiers();
    if (const auto iter = find(cbegin(factoryIdentifiers), cend(factoryIdentifiers), identifier);
        iter != cend(factoryIdentifiers)) {
      managerInterfaces.push_back(factory->instantiate(identifier));
    }
  }

  if (managerInterfaces.empty()) {
    throw errors::InputValidationException{fmt::format(
        "HybridPluginSystem: No plug-in registered with the identifier '{}'", identifier)};
  }

  if (managerInterfaces.size() == 1) {
    return std::move(managerInterfaces[0]);
  }

  return std::make_shared<HybridManagerInterface>(std::move(managerInterfaces));
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
