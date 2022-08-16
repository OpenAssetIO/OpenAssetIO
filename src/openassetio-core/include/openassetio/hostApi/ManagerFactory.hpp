// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <string>
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
    std::string displayName;
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
  static ManagerFactoryPtr make(
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
