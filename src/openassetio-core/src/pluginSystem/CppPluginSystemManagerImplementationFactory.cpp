// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <openassetio/pluginSystem/CppPluginSystemManagerImplementationFactory.hpp>

#include <cstdlib>
#include <memory>
#include <unordered_map>
#include <utility>

#include <fmt/format.h>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

namespace {
using ManagerPluginMap =
    std::unordered_map<openassetio::Str,
                       std::pair<std::filesystem::path, CppPluginSystemManagerPluginPtr>>;

[[maybe_unused]] ManagerPluginMap loadPlugins(const log::LoggerInterfacePtr& logger,
                                              const std::string_view paths) {
  auto pluginSystem = CppPluginSystem::make(logger);
  pluginSystem->scan(paths);

  ManagerPluginMap pluginMap;

  for (const openassetio::Identifier& identifier : pluginSystem->identifiers()) {
    const auto& [path, plugin] = pluginSystem->plugin(identifier);
    const auto managerPlugin = std::dynamic_pointer_cast<CppPluginSystemManagerPlugin>(plugin);
    if (!managerPlugin) {
      logger->log(log::LoggerInterface::Severity::kWarning,
                  fmt::format("Plugin '{}' from '{}' is not a CppPluginSystemManagerPlugin",
                              identifier, path.string()));
      continue;
    }

    pluginMap[identifier] = {path, managerPlugin};
  }

  return pluginMap;
}

}  // namespace

CppPluginSystemManagerImplementationFactory::Ptr CppPluginSystemManagerImplementationFactory::make(
    openassetio::Str paths, log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemManagerImplementationFactory>(
      CppPluginSystemManagerImplementationFactory{std::move(paths), std::move(logger)});
}

CppPluginSystemManagerImplementationFactory::Ptr CppPluginSystemManagerImplementationFactory::make(
    log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemManagerImplementationFactory>(
      CppPluginSystemManagerImplementationFactory{std::move(logger)});
}

CppPluginSystemManagerImplementationFactory::CppPluginSystemManagerImplementationFactory(
    openassetio::Str paths, log::LoggerInterfacePtr logger)
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
          []() -> openassetio::Str {
            if (auto* paths = std::getenv(kPluginEnvVar.data())) {
              return paths;
            }
            return {};
          }(),
          std::move(logger)} {}

Identifiers CppPluginSystemManagerImplementationFactory::identifiers() {
  return openassetio::Identifiers();
}

managerApi::ManagerInterfacePtr CppPluginSystemManagerImplementationFactory::instantiate(
    [[maybe_unused]] const Identifier& identifier) {
  return openassetio::managerApi::ManagerInterfacePtr();
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
