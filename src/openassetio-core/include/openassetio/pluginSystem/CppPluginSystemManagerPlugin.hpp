// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemManagerPlugin)

/**
 * Base class to be subclassed by plugins binding a @ref host to an @ref
 * asset_management_system.
 *
 * This is used by the dynamic plugin discovery mechanism to instantiate
 * the @ref managerApi.ManagerInterface "ManagerInterface"
 * implementation for the asset management system.
 *
 * Plugin authors must subclass this class and expose instances of it
 * via a @ref PluginFactory function pointer, which is in turn exposed
 * in the plugin binary by a top level C linkage `openassetioPlugin`
 * function.
 *
 * @see CppPluginSystemManagerImplementationFactory
 */
// NOLINTNEXTLINE(cppcoreguidelines-special-member-functions)
class OPENASSETIO_CORE_EXPORT CppPluginSystemManagerPlugin : public CppPluginSystemPlugin {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemManagerPlugin)

  /// Defaulted destructor.
  ~CppPluginSystemManagerPlugin() override;

  /**
   * Constructs an instance of the @ref managerApi.ManagerInterface
   * "ManagerInterface".
   *
   * This is an instance of some class derived from ManagerInterface
   * to be bound to the Host-facing @ref hostApi.Manager "Manager".
   *
   * Generally this is only directly called by the @ref
   * pluginSystem.CppPluginSystemManagerImplementationFactory
   * "CppPluginSystemManagerImplementationFactory".
   *
   * @return ManagerInterface instance
   */
  [[nodiscard]] virtual managerApi::ManagerInterfacePtr interface() = 0;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
