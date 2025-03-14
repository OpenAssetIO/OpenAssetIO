// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <openassetio/pluginSystem/CppPluginSystemManagerImplementationFactory.hpp>

#include <cstdlib>
#include <memory>
#include <optional>
#include <string_view>
#include <utility>

#include <fmt/core.h>

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

namespace {

const CppPluginSystem::ValidationCallback kCheckIsManagerPlugin{
    [](const CppPluginSystemPluginPtr& plugin) -> std::optional<Str> {
      if (!std::dynamic_pointer_cast<CppPluginSystemManagerPlugin>(plugin)) {
        return "It is not a manager plugin (CppPluginSystemManagerPlugin).";
      }
      return std::nullopt;
    }};

}  // namespace

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
    pluginSystem_->scan(paths_, kModuleHookName, kCheckIsManagerPlugin);
  }

  return pluginSystem_->identifiers();
}

managerApi::ManagerInterfacePtr CppPluginSystemManagerImplementationFactory::instantiate(
    const Identifier& identifier) {
  if (!pluginSystem_) {
    // Lazy load plugins.
    pluginSystem_ = CppPluginSystem::make(logger());
    pluginSystem_->scan(paths_, kModuleHookName, kCheckIsManagerPlugin);
  }
  const auto& [path, plugin] = pluginSystem_->plugin(identifier);

  // Should definitely be a manager plugin, as validated by
  // `kCheckIsManagerPlugin`. We use the exception-throwing version of
  // dynamic_cast just to be extra safe.
  auto& managerPlugin = dynamic_cast<CppPluginSystemManagerPlugin&>(*plugin);

  return managerPlugin.interface();
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
