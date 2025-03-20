// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once
#include <vector>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>

OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::pluginSystem {
OPENASSETIO_DECLARE_PTR(HybridPluginSystemUIDelegateImplementationFactory)

/**
 * The hybrid UI delegate plugin system composes one or more child
 * plugin systems, and selects the first plugin that matches the desired
 * identifier.
 *
 * A list of factories are provided in priority order. When a plugin
 * with a particular identifier is requested, factories are consulted
 * in the order they were provided to the constructor, and the first
 * factory that responds positively is used to construct the plugin.
 *
 * Although this class allows multiple plugin systems to be combined,
 * it does not support merging multiple matching plugins into one.
 * This is in contrast to the
 * @fqref{pluginSystem.HybridPluginSystemManagerImplementationFactory}
 * "hybrid manager plugin system".
 */
class OPENASSETIO_UI_EXPORT HybridPluginSystemUIDelegateImplementationFactory
    : public hostApi::UIDelegateImplementationFactoryInterface {
 public:
  using UIDelegateImplementationFactoryInterfaces =
      std::vector<hostApi::UIDelegateImplementationFactoryInterfacePtr>;

  OPENASSETIO_ALIAS_PTR(HybridPluginSystemUIDelegateImplementationFactory)

  /**
   * Construct a new instance.
   *
   * @param factories List of factories to compose.
   *
   * @param logger Logger for progress and warnings.
   *
   * @return New instance.
   */
  static HybridPluginSystemUIDelegateImplementationFactoryPtr make(
      UIDelegateImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger);

  /**
   * Get a list of all UI delegate plugin identifiers known to all child
   * factories.
   *
   * @return List of known UI delegate plugin identifiers.
   */
  Identifiers identifiers() override;

  /**
   * Create an instance of the @ref managerApi.UIDelegateInterface
   * "UIDelegateInterface" with the specified identifier.
   *
   * Note that, like any other plugin system, the returned
   * `UIDelegateInterface` cannot be used until @needsref
   * managerApi.UIDelegateInterface.initialize "initialized".
   *
   * Child factories are searched in the order they were provided to
   * the constructor, and the first factory that can instantiate a
   * plugin with the given @p identifier is used.
   *
   * @param identifier Identifier of the `UIDelegateInterface` to
   * instantiate.
   *
   * @return Newly created interface.
   *
   * @throws InputValidationException if the requested identifier has
   * not been registered as a UI delegate plugin.
   */
  managerApi::UIDelegateInterfacePtr instantiate(const Identifier& identifier) override;

 private:
  /// Private constructor. See @ref make.
  explicit HybridPluginSystemUIDelegateImplementationFactory(
      UIDelegateImplementationFactoryInterfaces factories, log::LoggerInterfacePtr logger);

  /// Child factories to compose.
  UIDelegateImplementationFactoryInterfaces factories_;
};
}  // namespace ui::pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
