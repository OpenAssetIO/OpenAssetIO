// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemUIDelegatePlugin)

/**
 * Base class to be subclassed by plugins binding a @ref host to a UI
 * delegate.
 *
 * This is used by the dynamic plugin discovery mechanism to instantiate
 * the @ref ui.managerApi.UIDelegateInterface "UIDelegateInterface"
 * implementation for the asset management system.
 *
 * Plugin authors must subclass this class and expose instances of it
 * via a @fqref{pluginSystem.PluginFactory} "PluginFactory" function
 * pointer, which is in turn exposed in the plugin binary by a top level
 * C linkage `openassetioUIPlugin` function.
 *
 * @see CppPluginSystemUIDelegateImplementationFactory
 */
// NOLINTNEXTLINE(cppcoreguidelines-special-member-functions)
class OPENASSETIO_UI_EXPORT CppPluginSystemUIDelegatePlugin
    : public openassetio::pluginSystem::CppPluginSystemPlugin {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemUIDelegatePlugin)

  /// Defaulted destructor.
  ~CppPluginSystemUIDelegatePlugin() override;

  /**
   * Constructs an instance of the @ref
   * ui.managerApi.UIDelegateInterface "UIDelegateInterface".
   *
   * This is an instance of some class derived from UIDelegateInterface
   * to be bound to the Host-facing @needsref ui.hostApi.UIDelegate
   * "UIDelegate".
   *
   * Generally this is only directly called by the @ref
   * ui.pluginSystem.CppPluginSystemUIDelegateImplementationFactory
   * "CppPluginSystemUIDelegateImplementationFactory".
   *
   * @return UIDelegateInterface instance
   */
  [[nodiscard]] virtual managerApi::UIDelegateInterfacePtr interface() = 0;
};
}  // namespace ui::pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
