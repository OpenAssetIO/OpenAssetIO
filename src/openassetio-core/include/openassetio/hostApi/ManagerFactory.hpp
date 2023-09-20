// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <string_view>
#include <unordered_map>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)
OPENASSETIO_FWD_DECLARE(hostApi, Manager)
OPENASSETIO_FWD_DECLARE(hostApi, ManagerImplementationFactoryInterface)
OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

OPENASSETIO_DECLARE_PTR(ManagerFactory)

/**
 * The ManagerFactory is the primary mechanism for querying for
 * available @ref manager "managers" and constructing a
 * @fqref{hostApi.Manager} "Manager".
 *
 * The underlying manager implementation is constructed using the
 * supplied \fqref{hostApi.ManagerImplementationFactoryInterface}
 * "ManagerImplementationFactoryInterface" factory implementation.
 *
 * Hosts should never attempt to directly construct a `Manager` class or
 * interact with the implementation factory directly.
 */
class OPENASSETIO_CORE_EXPORT ManagerFactory final {
 public:
  OPENASSETIO_ALIAS_PTR(ManagerFactory)

  /**
   * Simple struct containing the default configuration details of a
   * potential @ref manager implementation.
   */
  struct ManagerDetail {
    /**
     * Identifier of the manager.
     *
     * @see @fqref{hostApi.Manager.identifier} "Manager.identifier"
     */
    Identifier identifier;
    /**
     * Human readable display name of the manager, suitable for
     * presenting in a UI.
     *
     * @see @fqref{hostApi.Manager.displayName} "Manager.displayName"
     */
    Str displayName;
    /**
     * Arbitrary key-value information supplied by the manager.
     *
     * @see @fqref{hostApi.Manager.info} "Manager.info"
     */
    InfoDictionary info;
    /**
     * Compare all fields in this instance and another for by-value
     * equality.
     *
     * @param other Other instance to compare against.
     *
     * @return `true` if all fields compare equal, `false` otherwise.
     */
    bool operator==(const ManagerDetail& other) const {
      return identifier == other.identifier && displayName == other.displayName &&
             info == other.info;
    }
  };
  /// Mapping of manager identifier to its configuration details.
  using ManagerDetails = std::unordered_map<Identifier, ManagerDetail>;

  /**
   * The name of the env var used to define the default manager config TOML file.
    @see @ref defaultManagerForInterface.
   */
  static const Str kDefaultManagerConfigEnvVarName;

  /**
   * Construct an instance of this class.
   *
   * @param hostInterface The @ref host "host's" implementation of the
   * `HostInterface` that uniquely identifies the host and provides
   * common hooks for the @ref manager to query asset-related properties
   * from the host.
   *
   * @param managerImplementationFactory The factory that will be used to
   * instantiate managers. See, for example, @ref
   * pluginSystem.PythonPluginSystemManagerImplementationFactory.PythonPluginSystemManagerImplementationFactory
   * "PythonPluginSystemManagerImplementationFactory".
   *
   * @param logger The logger instance that will be used for all
   * messaging from the factory and instantiated @fqref{hostApi.Manager}
   * "Manager" instances.
   */
  [[nodiscard]] static ManagerFactoryPtr make(
      HostInterfacePtr hostInterface,
      ManagerImplementationFactoryInterfacePtr managerImplementationFactory,
      log::LoggerInterfacePtr logger);

  /**
   * All identifiers known to the factory.
   *
   * @note This may result in a significant amount of work being
   * performed by the supplied manager interface factory.
   *
   * @see @fqref{hostApi.Manager.identifier} "Manager.identifier".
   */
  [[nodiscard]] Identifiers identifiers() const;

  /**
   * Get the details for each available @ref manager as a map of
   * manager identifier to manager details.
   *
   * This provides the default settings that can be taken and mutated
   * before being used in the initialization of a
   * @fqref{hostApi.Manager} "Manager".
   *
   * Additional manager metadata is also included that may be useful.
   * For example, this may be presented as part of a manager picker UI
   * widget.
   *
   * @see @ref ManagerDetail
   *
   * @return A @ref ManagerDetail instance for each available @ref
   * manager.
   */
  [[nodiscard]] ManagerDetails availableManagers() const;

  /**
   * Create a @fqref{hostApi.Manager} "Manager" instance for the @ref
   * manager associated with the given identifier.
   *
   * The instance returned should then be used for all interaction with
   * the manager.
   *
   * @param identifier Unique manager identifier.
   *
   * @return Newly instantiated manager.
   */
  [[nodiscard]] ManagerPtr createManager(const Identifier& identifier) const;

  /**
   * Create a @fqref{hostApi.Manager} "Manager" instance for the @ref
   * manager associated with the given identifier.
   *
   * The instance returned should then be used for all interaction with
   * the manager.
   *
   * @param identifier Unique manager identifier.
   *
   * @param hostInterface The @ref host "host's" implementation of the
   * `HostInterface` that uniquely identifies the host and provides
   * common hooks for the @ref manager to query asset-related properties
   * from the host.
   *
   * @param managerImplementationFactory The factory that will be used to
   * instantiate the manager. See, for example, @ref
   * pluginSystem.PythonPluginSystemManagerImplementationFactory.PythonPluginSystemManagerImplementationFactory
   * "PythonPluginSystemManagerImplementationFactory".
   *
   * @param logger The logger instance that will be used for all
   * messaging from the factory and instantiated @fqref{hostApi.Manager}
   * "Manager" instances.
   *
   * @return Newly instantiated manager.
   */
  [[nodiscard]] static ManagerPtr createManagerForInterface(
      const Identifier& identifier, const HostInterfacePtr& hostInterface,
      const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
      const log::LoggerInterfacePtr& logger);

  /**
   * Creates the default @fqref{hostApi.Manager} "Manager" as defined by
   * the TOML configuration file referenced by the
   * @ref default_config_var.
   *
   * @note This mechanism should be the default approach for a host to
   * initialize the API. Extended functionality to override this
   * configuration can optionally be provided, but the ability to use
   * the shared, default configuration is always required.
   *
   * @see @ref defaultManagerForInterface(std::string_view, <!--
   * -->const HostInterfacePtr&,<!--
   * -->const ManagerImplementationFactoryInterfacePtr&,<!--
   * -->const log::LoggerInterfacePtr&) "Alternative direct signature"
   * for more details.
   *
   * @envvar **OPENASSETIO_DEFAULT_CONFIG** *str* The path to a
   * TOML file containing configuration information for the default
   * manager.
   *
   * @returns A default-configured manager if
   * @ref default_config_var is set, otherwise a nullptr if
   * the var was not set.
   *
   * @throws errors.InputValidationException if there are errors if the
   * config file does not exist at the path provided in the @ref
   * default_config_var env var.
   *
   * @throws errors.ConfigurationException if there are errors occur
   * whilst loading the TOML file referenced by the @ref
   * default_config_var env var.
   */
  [[nodiscard]] static ManagerPtr defaultManagerForInterface(
      const HostInterfacePtr& hostInterface,
      const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
      const log::LoggerInterfacePtr& logger);

  /**
   * Creates the default @fqref{hostApi.Manager} "Manager" as defined by
   * the given TOML configuration file.
   *
   * This allows deployments to centralize OpenAssetIO manager settings,
   * and for hosts to instantiate this manager without the need for
   * their own settings and persistence mechanism.
   *
   * The referenced TOML file should have the following structure.
   *
   * @code{.toml}
   * [manager]
   * identifier = "some.identifier"
   *
   * [manager.settings]  # Optional
   * some_setting = "value"
   * @endcode
   *
   * Any occurrences of `${config_dir}` within TOML string values will
   * be substituted with the absolute path to the directory containing
   * the TOML file, before being passed on to the manager settings.
   *
   * @param configPath Path to the TOML config file, compatible with
   * <a href="https://en.cppreference.com/w/cpp/io/basic_ifstream/open">
   * `std::ifstream::open`</a>. Relative paths resolve to a
   * platform/environment-dependent location.
   *
   * @param hostInterface The @ref host "host's" implementation of the
   * `HostInterface` that uniquely identifies the host and provides
   * common hooks for the @ref manager to query asset-related properties
   * from the host.
   *
   * @param managerImplementationFactory The factory that will be used
   * to instantiate managers.
   *
   * @param logger The logger instance that will be used for all
   * messaging from the instantiated @fqref{hostApi.Manager} "Manager"
   * instances.
   *
   * @return A default-configured manager.
   *
   * @throws errors.InputValidationException if there are errors if the
   * config file does not exist at the path provided in @p configPath.
   *
   * @throws errors.ConfigurationException if there are errors occur
   * whilst loading the TOML file.
   */
  [[nodiscard]] static ManagerPtr defaultManagerForInterface(
      std::string_view configPath, const HostInterfacePtr& hostInterface,
      const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
      const log::LoggerInterfacePtr& logger);

 private:
  ManagerFactory(HostInterfacePtr hostInterface,
                 ManagerImplementationFactoryInterfacePtr managerImplementationFactory,
                 log::LoggerInterfacePtr logger);

  const HostInterfacePtr hostInterface_;
  const ManagerImplementationFactoryInterfacePtr managerImplementationFactory_;
  const log::LoggerInterfacePtr logger_;
};

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
