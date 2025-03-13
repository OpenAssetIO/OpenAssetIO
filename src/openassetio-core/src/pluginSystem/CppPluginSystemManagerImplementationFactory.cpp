// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <openassetio/pluginSystem/CppPluginSystemManagerImplementationFactory.hpp>

#include <algorithm>
#include <cstdlib>
#include <memory>
#include <string_view>
#include <unordered_map>
#include <utility>

#include <fmt/core.h>
#include <fmt/format.h>

#include <openassetio/export.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

CppPluginSystemManagerImplementationFactoryPtr CppPluginSystemManagerImplementationFactory::make(
    Str paths, log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemManagerImplementationFactory>(
      CppPluginSystemManagerImplementationFactory{std::move(paths), std::move(logger)});
}

CppPluginSystemManagerImplementationFactoryPtr CppPluginSystemManagerImplementationFactory::make(
    log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemManagerImplementationFactory>(
      CppPluginSystemManagerImplementationFactory{std::move(logger)});
}

CppPluginSystemManagerImplementationFactory::CppPluginSystemManagerImplementationFactory(
    Str paths, log::LoggerInterfacePtr logger)
    : ManagerImplementationFactoryInterface{std::move(logger)}, paths_{std::move(paths)} {
  if (paths_.empty()) {
    this->logger()->log(
        log::LoggerInterface::Severity::kWarning,
        fmt::format("No search paths specified, no plugins will load - check ${} is set",
                    kPluginEnvVar));
  }
}

CppPluginSystemManagerImplementationFactory::CppPluginSystemManagerImplementationFactory(
    log::LoggerInterfacePtr logger)
    : CppPluginSystemManagerImplementationFactory{
          // getenv returns nullptr if var not set, which cannot be
          // used to construct a std::string.
          // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
          [paths = std::getenv(kPluginEnvVar.data())] { return paths ? paths : ""; }(),
          std::move(logger)} {}

Identifiers CppPluginSystemManagerImplementationFactory::identifiers() {
  if (!pluginSystem_) {
    // Lazy load plugins.
    pluginSystem_ = CppPluginSystem::make(logger());
    pluginSystem_->scan(paths_, kModuleHookName);
  }

  // Get all OpenAssetIO plugins, whether manager plugins or otherwise.
  Identifiers pluginIds = pluginSystem_->identifiers();

  // Filter plugins to only those that are manager plugins.
  pluginIds.erase(
      std::remove_if(
          begin(pluginIds), end(pluginIds),
          [&](const auto& identifier) {
            const auto& [path, plugin] = pluginSystem_->plugin(identifier);

            auto managerPlugin = std::dynamic_pointer_cast<CppPluginSystemManagerPlugin>(plugin);

            if (!managerPlugin) {
              logger()->log(
                  log::LoggerInterface::Severity::kWarning,
                  fmt::format(
                      "Plugin '{}' from '{}' is not a manager plugin as it cannot be cast to a"
                      " CppPluginSystemManagerPlugin",
                      identifier, path.string()));
            }

            return !managerPlugin;
          }),
      end(pluginIds));
  return pluginIds;
}

managerApi::ManagerInterfacePtr CppPluginSystemManagerImplementationFactory::instantiate(
    const Identifier& identifier) {
  if (!pluginSystem_) {
    // Lazy load plugins.
    pluginSystem_ = CppPluginSystem::make(logger());
    pluginSystem_->scan(paths_, kModuleHookName);
  }
  const auto& [path, plugin] = pluginSystem_->plugin(identifier);

  auto managerPlugin = std::dynamic_pointer_cast<CppPluginSystemManagerPlugin>(plugin);

  if (!managerPlugin) {
    throw errors::InputValidationException{
        fmt::format("Plugin '{}' from '{}' is not a manager plugin as it cannot be cast to a"
                    " CppPluginSystemManagerPlugin",
                    identifier, path.string())};
  }

  return managerPlugin->interface();
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
