// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once
#include <filesystem>
#include <optional>
#include <unordered_map>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(pluginSystem, CppPluginSystemManagerPlugin)
OPENASSETIO_FWD_DECLARE(pluginSystem, CppPluginSystem)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemManagerImplementationFactory)

/**
 * A factory to manage @ref CppPluginSystemManagerPlugin derived
 * plugins.
 *
 * This class is not usually used directly by a @ref host, which instead
 * uses the @ref hostApi.ManagerFactory "ManagerFactory".
 *
 * The factory loads plugins found under paths specified in the
 * `OPENASSETIO_PLUGIN_PATH` env var.
 *
 * @envvar **OPENASSETIO_PLUGIN_PATH** *str* A **PATH**-style list of
 * directories to search for
 * @fqref{pluginSystem.CppPluginSystemManagerPlugin}
 * "CppPluginSystemManagerPlugin" based plugins. It uses the
 * platform-native delimiter. Searched left to right. Note that this
 * environment variable is also used by the @ref
 * openassetio.pluginSystem.PythonPluginSystemManagerImplementationFactory
 * "PythonPluginSystemManagerImplementationFactory".
 *
 * Plugins are scanned and loaded lazily when required. In particular,
 * this means no plugin scanning is done on construction.
 *
 * @see CppPluginSystem
 * @see CppPluginSystemManagerPlugin
 */
class OPENASSETIO_CORE_EXPORT CppPluginSystemManagerImplementationFactory
    : public hostApi::ManagerImplementationFactoryInterface {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemManagerImplementationFactory)

  /// Environment variable to read the plugin search path from.
  static constexpr std::string_view kPluginEnvVar = "OPENASSETIO_PLUGIN_PATH";
  /// Name of entry point function to locate within discovered paths.
  static constexpr std::string_view kModuleHookName = "openassetioPlugin";

  /**
   * Construct a new instance.
   *
   * Plugin search path(s) will be taken from the @ref kPluginEnvVar
   * environment variable.
   *
   * @param logger Logger for progress and warnings.
   *
   * @return New instance.
   */
  static CppPluginSystemManagerImplementationFactoryPtr make(log::LoggerInterfacePtr logger);

  /**
   * Construct a new instance.
   *
   * The @ref kPluginEnvVar environment variable will be ignored.
   *
   * @param paths Plugin search paths.
   *
   * @param logger Logger for progress and warnings.
   *
   * @return New instance.
   */
  static Ptr make(openassetio::Str paths, log::LoggerInterfacePtr logger);

  /**
   * Get a list of all manager plugin identifiers known to the factory.
   *
   * @return List of known manager plugin identifiers.
   */
  Identifiers identifiers() override;

  /**
   * Create an instance of the @fqref{managerApi.ManagerInterface}
   * "ManagerInterface" with the specified identifier.
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
  explicit CppPluginSystemManagerImplementationFactory(log::LoggerInterfacePtr logger);
  /// Private constructor. See @ref make.
  CppPluginSystemManagerImplementationFactory(openassetio::Str paths,
                                              log::LoggerInterfacePtr logger);

  /// Search paths provided on construction.
  openassetio::Str paths_;

  /**
   * Underlying plugin system for loading generic OpenAssetIO plugins.
   *
   * Plugins reported by the plugin system are further filtered such
   * that only those that expose a @ref CppPluginSystemManagerPlugin
   * are considered.
   */
  CppPluginSystemPtr pluginSystem_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
