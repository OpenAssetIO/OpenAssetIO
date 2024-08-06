// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once
#include <vector>

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {
OPENASSETIO_DECLARE_PTR(HybridPluginSystemManagerImplementationFactory)

/**
 * The hybrid plugin system composes one or more child plugin systems,
 * and abstracts away routing API calls based on priority and
 * capability.
 *
 * A list of factories are provided in priority order. When a plugin
 * with a particular identifier is requested, all factories are queried
 * and any that return positively for the identifier have their
 * resulting @ref managerApi.ManagerInterface "ManagerInterface"
 * instances composed into a single `ManagerInterface`, such that API
 * calls are dispatched to the appropriate child instance, based on
 * priority and capability.
 *
 * Manager plugins advertise their capabilities using @ref
 * managerApi.ManagerInterface.hasCapability
 * "ManagerInterface.hasCapability".
 *
 * If multiple plugins support the same capability, then priority is
 * given to the plugin corresponding to the earliest in the list of
 * provided child factories.
 */
class OPENASSETIO_CORE_EXPORT HybridPluginSystemManagerImplementationFactory
    : public hostApi::ManagerImplementationFactoryInterface {
 public:
  using ManagerImplementationFactoryInterfaces =
      std::vector<hostApi::ManagerImplementationFactoryInterfacePtr>;

  OPENASSETIO_ALIAS_PTR(HybridPluginSystemManagerImplementationFactory)

  /**
   * Construct a new instance.
   *
   * @param factories List of factories to compose.
   *
   * @param logger Logger for progress and warnings.
   *
   * @return New instance.
   */
  static HybridPluginSystemManagerImplementationFactoryPtr make(
      ManagerImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger);

  /**
   * Get a list of all manager plugin identifiers known to all child
   * factories.
   *
   * @return List of known manager plugin identifiers.
   */
  Identifiers identifiers() override;

  /**
   * Create an instance of the @ref managerApi.ManagerInterface
   * "ManagerInterface" with the specified identifier.
   *
   * If multiple factories return a positive result for the identifier,
   * composition is performed to create a single @ref
   * managerApi.ManagerInterface "ManagerInterface" that dispatches API
   * calls to the appropriate child instance, based on advertised
   * capability or priority order.
   *
   * Note that, like any other plugin system, the returned
   * `ManagerInterface` cannot be used until @ref
   * managerApi.ManagerInterface.initialize "initialized".
   *
   * @param identifier Identifier of the `ManagerInterface` to
   * instantiate.
   *
   * @return Newly created interface.
   *
   * @throws InputValidationException if the requested identifier has
   * not been registered as a manager plugin.
   */
  managerApi::ManagerInterfacePtr instantiate(const Identifier& identifier) override;

 private:
  /// Private constructor. See @ref make.
  explicit HybridPluginSystemManagerImplementationFactory(
      ManagerImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger);

  /// Child factories to compose.
  ManagerImplementationFactoryInterfaces factories_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
