// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <algorithm>
#include <sstream>
#include <string>
#include <string_view>

#include <export.h>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/trait/TraitsData.hpp>

// Unique ID of the plugin.
constexpr std::string_view kPluginId = "org.openassetio.examples.manager.simplecppmanager";
// Settings keys.
constexpr std::string_view kSettingsKeyForEntityRefPrefix = "prefix";
constexpr std::string_view kSettingsKeyForCapabilities = "capabilities";
constexpr std::string_view kSettingsKeyForReadPolicy = "read_policy";
constexpr std::string_view kSettingsKeyForReadEntityTraitProperties = "read_traits";

/**
 * Simple manager implementation.
 *
 * This simple manager regurgitates values that are encoded in the
 * settings dictionary. In particular, the settings can contain a
 * list of entity references and their associated traits and properties,
 * encoded as a CSV document.
 *
 * Only the required set of capabilities plus "resolution" are
 * implemented and advertised by default. Any capability can be enabled,
 * however, to aid in downstream testing. Unsupported methods will then
 * return a stub response, rather than throw a
 * `NotImplementedException`.
 *
 * @see initialize
 */
struct SimpleCppManagerInterface final : openassetio::managerApi::ManagerInterface {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return openassetio::Identifier{kPluginId};
  }

  /**
   * Override the initialize method to parse settings for data to
   * regurgitate.
   *
   * The "database" of entities is specified as a CSV document in the
   * settings dict.
   *
   * Similarly other settings are available to make this manager more
   * puppetable. These include:
   * - "prefix" - Prefix for entity references.
   * - "capabilities" - CSV list of capabilities.
   * - "read_policy" - Trait for successful managementPolicy queries.
   * - "read_traits" - CSV document of entity trait properties.
   *
   * Typically these settings are provided by the toml config file (see
   * OPENASSETIO_DEFAULT_CONFIG), but they can also be provided by the
   * host application (including as part of a re-`initialize`), or as
   * fixtures in the openassetio.test.manager API compliance test suite.
   */
  void initialize(
      openassetio::InfoDictionary managerSettings,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    // Update stored settings with changes from the host.
    // Note that `merge` does not overwrite existing keys, so we must
    // do a little dance.
    managerSettings.merge(std::move(settings_));
    settings_ = std::move(managerSettings);

    // Allow a configurable entity reference prefix.
    if (const auto& keyAndValue = settings_.find(openassetio::Str{kSettingsKeyForEntityRefPrefix});
        keyAndValue != cend(settings_)) {
      entityReferencePrefix_ = std::get<openassetio::Str>(keyAndValue->second);
    }

    // Support customisable capabilities. Assume a single-row CSV
    // format.
    if (const auto& keyAndValue = settings_.find(openassetio::Str{kSettingsKeyForCapabilities});
        keyAndValue != cend(settings_)) {
      std::istringstream csvRowAsStream{std::get<openassetio::Str>(keyAndValue->second)};
      std::string capability;
      while (std::getline(csvRowAsStream, capability, ',')) {
        if (const auto& iter = find(cbegin(kCapabilityNames), cend(kCapabilityNames), capability);
            iter != cend(kCapabilityNames)) {
          capabilities_.insert(static_cast<ManagerInterface::Capability>(
              std::distance(cbegin(kCapabilityNames), iter)));
        } else {
          throw openassetio::errors::ConfigurationException(
              "SimpleCppManager: unsupported capability: " + capability);
        }
      }
    }

    // For successful kRead managementPolicy queries, return the
    // following policy trait alongside the queried traits.
    if (const auto& keyAndValue = settings_.find(openassetio::Str{kSettingsKeyForReadPolicy});
        keyAndValue != cend(settings_)) {
      readPolicy_ = std::get<openassetio::Str>(keyAndValue->second);
    }

    // The database of entities is specified as a CSV document.

    if (const auto& keyAndValue =
            settings_.find(openassetio::Str{kSettingsKeyForReadEntityTraitProperties});
        keyAndValue != cend(settings_)) {
      // Loop over CSV document rows.
      std::istringstream csvAsStream(std::get<openassetio::Str>(keyAndValue->second));
      std::string csvRow;
      while (std::getline(csvAsStream, csvRow)) {
        std::istringstream csvRowAsStream(csvRow);
        std::string entityRef;
        std::string traitId;
        std::string propertyKey;
        std::string propertyValue;
        std::getline(csvRowAsStream, entityRef, ',');
        std::getline(csvRowAsStream, traitId, ',');
        std::getline(csvRowAsStream, propertyKey, ',');
        std::getline(csvRowAsStream, propertyValue, ',');
        Properties& properties = entityTraitProperties_[std::move(entityRef)][std::move(traitId)];
        if (!propertyKey.empty()) {
          properties[std::move(propertyKey)] = std::move(propertyValue);
        }
      }
    }
  }

  [[nodiscard]] openassetio::InfoDictionary settings(
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    return settings_;
  }

  [[nodiscard]] openassetio::Str displayName() const override { return "Simple C++ Manager"; }

  [[nodiscard]] bool hasCapability(const Capability capability) override {
    return capabilities_.count(capability) != 0U;
  }

  /**
   * Override to provide policy based on configuration.
   *
   * For each trait set in @p traitSets, determine if any entity in the
   * database has all the traits in the set. If so, the corresponding
   * entry in the result should be imbued will all those traits
   * (excluding those without any properties), plus the policy trait (if
   * configured). Otherwise, the entry should be empty.
   *
   * Only read access is supported.
   */
  [[nodiscard]] openassetio::trait::TraitsDatas managementPolicy(
      const openassetio::trait::TraitSets& traitSets,
      const openassetio::access::PolicyAccess policyAccess,
      [[maybe_unused]] const openassetio::ContextConstPtr& context,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    namespace trait = openassetio::trait;

    // Initialize the result with empty TraitsData entries.
    trait::TraitsDatas result;
    result.reserve(traitSets.size());
    std::generate_n(std::back_inserter(result), traitSets.size(),
                    [] { return trait::TraitsData::make(); });

    // We only support read.
    if (policyAccess != openassetio::access::PolicyAccess::kRead) {
      return result;
    }

    // Helper function to determine if a trait set is a subset of the
    // traits of an entity.
    // NOLINTNEXTLINE(readability-identifier-naming)
    static constexpr auto isSubsetOfEntityTraitSet = [](const TraitProperties& traitIdToProperties,
                                                        const trait::TraitSet& traitSet) {
      return std::all_of(cbegin(traitSet), cend(traitSet),
                         [&traitIdToProperties](const trait::TraitId& desiredTraitId) {
                           return traitIdToProperties.count(desiredTraitId);
                         });
    };

    // Loop over each trait set in the input batch.
    for (std::size_t idx = 0; idx < traitSets.size(); ++idx) {
      const trait::TraitSet& traitSet = traitSets[idx];

      // An empty trait set is the least possible specificity, i.e.
      // asking "do you manage everything?", which we don't.
      if (traitSet.empty()) {
        continue;
      }

      const trait::TraitsDataPtr& traitsData = result[idx];

      for (const auto& entityRefAndTraitProperties : entityTraitProperties_) {
        // If the entity has all the traits in the set, then this trait
        // set is supported.

        if (isSubsetOfEntityTraitSet(entityRefAndTraitProperties.second, traitSet)) {
          for (const trait::TraitId& traitId : traitSet) {
            // We only imbue traits that have properties that can be
            // `resolve`d.
            if (!entityRefAndTraitProperties.second.at(traitId).empty()) {
              traitsData->addTrait(traitId);
            }
          }

          // Policy traits can be used to communicate policy-specific
          // information.
          if (!readPolicy_.empty()) {
            traitsData->addTrait(readPolicy_);
          }
          break;
        }
      }
    }

    return result;
  }

  /**
   * Override to check string based on configured prefix.
   *
   * Prefix must be provided by the "prefix" setting.
   */
  [[nodiscard]] bool isEntityReferenceString(
      const openassetio::Str& someString,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    return someString.rfind(entityReferencePrefix_, 0) == 0;
  }

  /**
   * Override to retrieve the traits of provided entities from the
   * database.
   *
   * Only read access is supported.
   */
  void entityTraits(const openassetio::EntityReferences& entityReferences,
                    const openassetio::access::EntityTraitsAccess entityTraitsAccess,
                    [[maybe_unused]] const openassetio::ContextConstPtr& context,
                    [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
                    const EntityTraitsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback) override {
    namespace trait = openassetio::trait;
    using openassetio::errors::BatchElementError;

    // We only support read access.
    if (entityTraitsAccess != openassetio::access::EntityTraitsAccess::kRead) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        errorCallback(idx, BatchElementError{BatchElementError::ErrorCode::kEntityAccessError,
                                             "Entity access is read-only"});
      }
      return;
    }

    // Loop each entity reference in the input batch.
    for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
      const openassetio::EntityReference& entityReference = entityReferences[idx];

      // Find the entity reference in the database.
      if (const auto entityRefAndTraitProperties =
              entityTraitProperties_.find(entityReference.toString());
          entityRefAndTraitProperties != cend(entityTraitProperties_)) {
        // Construct the trait set for the entity.
        trait::TraitSet traitSet;
        std::transform(
            cbegin(entityRefAndTraitProperties->second), cend(entityRefAndTraitProperties->second),
            std::inserter(traitSet, end(traitSet)),
            [](const auto& traitIdAndProperties) { return traitIdAndProperties.first; });
        successCallback(idx, std::move(traitSet));
      } else {
        // If we can't find the entity reference in the database, then
        // flag an error.
        errorCallback(idx, BatchElementError{BatchElementError::ErrorCode::kEntityResolutionError,
                                             "Entity not found"});
      }
    }
  }

  /**
   * Override to retrieve the properties of provided entities from the
   * database.
   *
   * Only read access is supported.
   */
  void resolve(const openassetio::EntityReferences& entityReferences,
               const openassetio::trait::TraitSet& traitSet,
               const openassetio::access::ResolveAccess resolveAccess,
               [[maybe_unused]] const openassetio::ContextConstPtr& context,
               [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
               const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback) override {
    namespace trait = openassetio::trait;
    using openassetio::errors::BatchElementError;

    // We only support read access.
    if (resolveAccess != openassetio::access::ResolveAccess::kRead) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        errorCallback(idx, BatchElementError{BatchElementError::ErrorCode::kEntityAccessError,
                                             "Entity access is read-only"});
      }
      return;
    }

    // Loop each entity reference in the input batch.
    for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
      const openassetio::EntityReference& entityReference = entityReferences[idx];

      // Find the entity reference in the database.
      if (const auto& entityRefAndTraitProperties =
              entityTraitProperties_.find(entityReference.toString());
          entityRefAndTraitProperties != cend(entityTraitProperties_)) {
        trait::TraitsDataPtr traitsData = trait::TraitsData::make();

        // Set the properties for the traits, converting from str to
        // numeric/boolean as necessary.
        for (const trait::TraitId& traitId : traitSet) {
          // Check if the entity has the requested trait.
          if (const auto& traitAndProperties = entityRefAndTraitProperties->second.find(traitId);
              traitAndProperties != cend(entityRefAndTraitProperties->second)) {
            // Set all properties for the trait. Note that we rely on
            // this to implicitly imbue the trait, meaning the trait
            // remains unimbued if it has no associated properties.
            for (const auto& [propertyKey, propertyValueAsStr] : traitAndProperties->second) {
              traitsData->setTraitProperty(traitId, propertyKey,
                                           strToPropertyValue(propertyValueAsStr));
            }
          }
        }

        successCallback(idx, std::move(traitsData));
      } else {
        // If we can't find the entity reference in the database, then
        // flag an error.
        errorCallback(idx, BatchElementError{BatchElementError::ErrorCode::kEntityResolutionError,
                                             "Entity not found"});
      }
    }
  }

  //////////////////////////////////////////////////////////////////////
  /*
   * The following methods either call the base class implementation or
   * return a stub response, depending on the configured capabilities.
   *
   * Note that the base class implementation will throw a
   * `NotImplementedException`.
   */

  [[nodiscard]] openassetio::StrMap updateTerminology(
      [[maybe_unused]] openassetio::StrMap terms,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    if (hasCapability(Capability::kCustomTerminology)) {
      return {};
    }
    return ManagerInterface::updateTerminology(std::move(terms), hostSession);
  }
  [[nodiscard]] openassetio::managerApi::ManagerStateBasePtr createState(
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    if (hasCapability(Capability::kStatefulContexts)) {
      return {};
    }
    return ManagerInterface::createState(hostSession);
  }
  [[nodiscard]] openassetio::managerApi::ManagerStateBasePtr createChildState(
      [[maybe_unused]] const openassetio::managerApi::ManagerStateBasePtr& parentState,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    if (hasCapability(Capability::kStatefulContexts)) {
      return {};
    }
    return ManagerInterface::createChildState(parentState, hostSession);
  }
  [[nodiscard]] openassetio::Str persistenceTokenForState(
      [[maybe_unused]] const openassetio::managerApi::ManagerStateBasePtr& state,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    if (hasCapability(Capability::kStatefulContexts)) {
      return "a";
    }
    return ManagerInterface::persistenceTokenForState(state, hostSession);
  }
  [[nodiscard]] openassetio::managerApi::ManagerStateBasePtr stateFromPersistenceToken(
      [[maybe_unused]] const openassetio::Str& token,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
    if (hasCapability(Capability::kStatefulContexts)) {
      return {};
    }
    return ManagerInterface::stateFromPersistenceToken(token, hostSession);
  }
  void entityExists(const openassetio::EntityReferences& entityReferences,
                    [[maybe_unused]] const openassetio::ContextConstPtr& context,
                    [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
                    const ExistsSuccessCallback& successCallback,
                    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kExistenceQueries)) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        successCallback(idx, false);
      }
    } else {
      ManagerInterface::entityExists(entityReferences, context, hostSession, successCallback,
                                     errorCallback);
    }
  }
  void defaultEntityReference(
      const openassetio::trait::TraitSets& traitSets,
      [[maybe_unused]] const openassetio::access::DefaultEntityAccess defaultEntityAccess,
      [[maybe_unused]] const openassetio::ContextConstPtr& context,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
      const DefaultEntityReferenceSuccessCallback& successCallback,
      [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kDefaultEntityReferences)) {
      for (std::size_t idx = 0; idx < traitSets.size(); ++idx) {
        successCallback(idx, openassetio::EntityReference(entityReferencePrefix_));
      }
    } else {
      ManagerInterface::defaultEntityReference(traitSets, defaultEntityAccess, context,
                                               hostSession, successCallback, errorCallback);
    }
  }
  void getWithRelationship(
      const openassetio::EntityReferences& entityReferences,
      [[maybe_unused]] const openassetio::trait::TraitsDataPtr& relationshipTraitsData,
      [[maybe_unused]] const openassetio::trait::TraitSet& resultTraitSet,
      [[maybe_unused]] const size_t pageSize,
      [[maybe_unused]] const openassetio::access::RelationsAccess relationsAccess,
      [[maybe_unused]] const openassetio::ContextConstPtr& context,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
      const RelationshipQuerySuccessCallback& successCallback,
      [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kRelationshipQueries)) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        successCallback(idx, std::make_shared<StubPager>());
      }
    } else {
      ManagerInterface::getWithRelationship(entityReferences, relationshipTraitsData,
                                            resultTraitSet, pageSize, relationsAccess, context,
                                            hostSession, successCallback, errorCallback);
    }
  }
  void getWithRelationships(
      [[maybe_unused]] const openassetio::EntityReference& entityReference,
      const openassetio::trait::TraitsDatas& relationshipTraitsDatas,
      [[maybe_unused]] const openassetio::trait::TraitSet& resultTraitSet,
      [[maybe_unused]] const size_t pageSize,
      [[maybe_unused]] const openassetio::access::RelationsAccess relationsAccess,
      [[maybe_unused]] const openassetio::ContextConstPtr& context,
      [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
      const RelationshipQuerySuccessCallback& successCallback,
      [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kRelationshipQueries)) {
      for (std::size_t idx = 0; idx < relationshipTraitsDatas.size(); ++idx) {
        successCallback(idx, std::make_shared<StubPager>());
      }
    } else {
      ManagerInterface::getWithRelationships(entityReference, relationshipTraitsDatas,
                                             resultTraitSet, pageSize, relationsAccess, context,
                                             hostSession, successCallback, errorCallback);
    }
  }
  void preflight(const openassetio::EntityReferences& entityReferences,
                 [[maybe_unused]] const openassetio::trait::TraitsDatas& traitsHints,
                 [[maybe_unused]] const openassetio::access::PublishingAccess publishingAccess,
                 [[maybe_unused]] const openassetio::ContextConstPtr& context,
                 [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
                 const PreflightSuccessCallback& successCallback,
                 [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kPublishing)) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        successCallback(idx, entityReferences[idx]);
      }
    } else {
      ManagerInterface::preflight(entityReferences, traitsHints, publishingAccess, context,
                                  hostSession, successCallback, errorCallback);
    }
  }
  void register_(const openassetio::EntityReferences& entityReferences,
                 [[maybe_unused]] const openassetio::trait::TraitsDatas& entityTraitsDatas,
                 [[maybe_unused]] const openassetio::access::PublishingAccess publishingAccess,
                 [[maybe_unused]] const openassetio::ContextConstPtr& context,
                 [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
                 const RegisterSuccessCallback& successCallback,
                 [[maybe_unused]] const BatchElementErrorCallback& errorCallback) override {
    if (hasCapability(Capability::kPublishing)) {
      for (std::size_t idx = 0; idx < entityReferences.size(); ++idx) {
        successCallback(idx, entityReferences[idx]);
      }
    } else {
      ManagerInterface::register_(entityReferences, entityTraitsDatas, publishingAccess, context,
                                  hostSession, successCallback, errorCallback);
    }
  }

 private:
  /**
   * Helper function to convert a string to a property value, i.e. a
   * variant of int, float, bool, or string.
   *
   * When using std::stringstream, it is insufficient to check that
   * conversion succeeds - we must also ensure the whole input is
   * consumed. E.g. 123.4 will parse as an int and leave the .4
   * unconsumed. Detecting that we've consumed the input using .eof()
   * doesn't work for boolean conversions (because it doesn't consume to
   * eof), and using .tellg() doesn't work for numeric conversions
   * (because it consumes to eof). Luckily .peek() works in all cases.
   *
   * In order to fully reset the state of the stringstream between
   * conversion attempts, it's easiest just to reconstruct it from
   * scratch.
   */
  static openassetio::trait::property::Value strToPropertyValue(const std::string& valueAsString) {
    static constexpr auto kEof = std::stringstream::traits_type::eof();
    std::stringstream converter;

    // Attempt integer conversion.
    converter = std::stringstream{valueAsString};
    if (openassetio::Int result; (converter >> result) && (converter.peek() == kEof)) {
      return result;
    }

    // Attempt float conversion.
    converter = std::stringstream{valueAsString};
    if (openassetio::Float result; (converter >> result) && (converter.peek() == kEof)) {
      return result;
    }

    // Attempt boolean conversion (from "true"/"false" strings).
    converter = std::stringstream{valueAsString};
    if (openassetio::Bool result;
        (converter >> std::boolalpha >> result) && (converter.peek() == kEof)) {
      return result;
    }

    // Assume it's just a string.
    return valueAsString;
  };

  /**
   * Stub pager that always returns an empty list of entity references.
   *
   * Required for the getWithRelationship(s) methods.
   */
  struct StubPager final : openassetio::managerApi::EntityReferencePagerInterface {
    void close(
        [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {}
    [[nodiscard]] bool hasNext(
        [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
      return false;
    }
    [[nodiscard]] openassetio::EntityReferences get(
        [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {
      return {};
    }
    void next(
        [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) override {}
  };

  /// Settings dictionary as provided to `initialize`.
  openassetio::InfoDictionary settings_;

  /**
   * Capabilities that are supported by this manager.
   *
   * The default set here is the only properly implemented (i.e.
   * non-stub) functionality. Capabilities can be toggled using the
   * "capabilities" key in @ref settings_.
   */
  std::unordered_set<ManagerInterface::Capability> capabilities_{
      Capability::kEntityReferenceIdentification, Capability::kManagementPolicyQueries,
      Capability::kEntityTraitIntrospection, Capability::kResolution};

  /**
   * Key-value properties for entities and their traits.
   *
   * The string value will be coerced to the appropriate type when
   * the property is resolved.
   */
  using Properties = std::unordered_map<std::string, std::string>;
  /// Map of trait IDs to properties.
  using TraitProperties = std::unordered_map<std::string, Properties>;
  /// Map of entity references to trait IDs and their properties.
  using EntityTraitProperties = std::unordered_map<std::string, TraitProperties>;

  /// The entity database.
  EntityTraitProperties entityTraitProperties_;

  /// Prefix for entity references. Used in @ref
  /// isEntityReferenceString.
  std::string entityReferencePrefix_{"simplecpp://"};

  /// Additional policy trait to imbue in the response to successful
  /// managementPolicy queries.
  openassetio::trait::TraitId readPolicy_;
};

/**
 * Subclass of the CppPluginSystemManagerPlugin that can be used to
 * construct instances of our simple ManagerInterface.
 */
struct Plugin final : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return openassetio::Identifier{kPluginId};
  }
  openassetio::managerApi::ManagerInterfacePtr interface() override {
    return std::make_shared<SimpleCppManagerInterface>();
  }
};

extern "C" {

/**
 * External entry point that the OpenAssetIO plugin system will query.
 *
 * For cross-platform compatibility there are a few layers of
 * indirection in loading a plugin. First, this C linkage function is
 * called, which returns a factory function. The factory, when called,
 * returns a reference to a generic plugin object. The plugin object is
 * a subclass instance that provides methods for creating a manager
 * interface.
 *
 * @return A lambda that will create an instance of a generic plugin
 * object.
 */
OPENASSETIO_EXAMPLE_SIMPLECPPMANAGER_EXPORT
openassetio::pluginSystem::PluginFactory openassetioPlugin() noexcept {
  return []() noexcept -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<Plugin>();
  };
}
}
