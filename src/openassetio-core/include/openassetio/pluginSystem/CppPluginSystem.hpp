// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#pragma once
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(pluginSystem, CppPluginSystemPlugin)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystem)

/**
 * Generic plugin system for C++ plugins.
 *
 * The API broadly mirrors the @ref pluginSystem.PythonPluginSystem
 * "PythonPluginSystem".
 *
 * @see @ref scan
 * @see @ref PluginFactory
 * @see @ref CppPluginSystemPlugin
 */
class OPENASSETIO_CORE_EXPORT CppPluginSystem {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystem)
  /// Pair of absolute path to plugin and shared_ptr to plugin instance.
  using PathAndPlugin = std::pair<std::filesystem::path, CppPluginSystemPluginPtr>;

  /**
   * Constructs a new CppPluginSystem.
   *
   * @param logger Logger used to log progress and warnings. Note that
   * most logs are at @ref log.LoggerInterface.Severity.kDebug "debug"
   * severity.
   *
   * @return Newly constructed CppPluginSystem wrapped in a shared_ptr.
   */
  static CppPluginSystemPtr make(log::LoggerInterfacePtr logger);

  /**
   * Clear any previously loaded plugins.
   *
   * Note this does not unload/unlink any previously loaded binary
   * shared libraries from the application.
   */
  void reset();

  /**
   * Callback provided to @ref scan to provide further validation.
   *
   * A return value of empty optional signals that the plugin is OK.
   * A return value of a string signals that the plugin is not OK and
   * the string provides the reason.
   */
  using ValidationCallback = std::function<std::optional<Str>(const CppPluginSystemPluginPtr&)>;

  /**
   * Searches the supplied paths for plugin modules.
   *
   * Paths are searched left-to-right, but only the first instance of
   * any given plugin identifier will be used, and subsequent
   * registrations ignored. This means entries to the left of the
   * paths list take precedence over ones to the right.
   *
   * @note Precedence order is undefined for plugins sharing the
   * same identifier within the same directory.
   *
   * Each given directory is scanned for shared libraries that expose a
   * given hook function (with C linkage), which is expected to return a
   * @ref PluginFactory function pointer, which when called returns an
   * instantiated (subclass of) @ref CppPluginSystemPlugin.
   *
   * Discovered plugins are registered by their exposed identifier, and
   * subsequent registrations with the same identifier will be skipped.
   *
   * No attempt is made to catch exceptions during static initialisation
   * or during the call to the provided @ref PluginFactory, and any such
   * exception will almost definitely terminate the process.
   *
   * @param paths A list of paths to search, delimited by operating
   * system specific path separator (i.e. `:` for POSIX, `;` for
   * Windows).
   *
   * @param moduleHookName The name of the entry point function to scan
   * for and execute within discovered files.
   *
   * @param validationCallback A callback that will be given a candidate
   * CppPluginSystemPtr and should return an empty optional if the
   * plugin is valid, or a reason string if not valid.
   */
  void scan(std::string_view paths, std::string_view moduleHookName,
            const ValidationCallback& validationCallback);

  /**
   * Returns the identifiers known to the plugin system.
   *
   * If @ref scan has not been called, then this will be empty.
   */
  [[nodiscard]] openassetio::Identifiers identifiers() const;

  /**
   * Retrieves the plugin that provides the given identifier.
   *
   * @param identifier Identifier to look up.
   *
   * @return A pair of plugin path and instance.
   *
   * @exception errors.InputValidationException Raised if no plugin
   * provides the specified identifier.
   */
  const PathAndPlugin& plugin(const openassetio::Identifier& identifier) const;

 private:
  /// Mapping of plugin identifier to file path and instance.
  using PluginMap = std::unordered_map<openassetio::Identifier, PathAndPlugin>;
  /// Optional pair of plugin identifier and instance.
  using MaybeIdentifierAndPlugin =
      std::optional<std::pair<openassetio::Identifier, CppPluginSystemPluginPtr>>;
  /// Attempt to load a plugin at a given path, returning nullopt on
  /// failure.
  MaybeIdentifierAndPlugin maybeLoadPlugin(const std::filesystem::path& filePath,
                                           std::string_view moduleHookName,
                                           const ValidationCallback& validationCallback);

  /// Private constructor. See @ref make.
  explicit CppPluginSystem(log::LoggerInterfacePtr logger);

  /// Logger for logging progress, warnings and errors.
  log::LoggerInterfacePtr logger_;
  /// Map of discovered plugin identifiers to their file path and
  /// instance.
  PluginMap plugins_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
