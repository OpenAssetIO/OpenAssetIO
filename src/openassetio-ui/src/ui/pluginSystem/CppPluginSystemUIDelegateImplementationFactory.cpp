// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/pluginSystem/CppPluginSystemUIDelegateImplementationFactory.hpp>

#include <cstdlib>
#include <memory>
#include <optional>
#include <string_view>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
#include <openassetio/ui/pluginSystem/CppPluginSystemUIDelegatePlugin.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::pluginSystem {

namespace {
using openassetio::pluginSystem::CppPluginSystem;
using openassetio::pluginSystem::CppPluginSystemPluginPtr;

const CppPluginSystem::ValidationCallback kCheckIsUIDelegatePlugin{
    [](const CppPluginSystemPluginPtr& plugin) -> std::optional<Str> {
      if (!std::dynamic_pointer_cast<CppPluginSystemUIDelegatePlugin>(plugin)) {
        return "It is not a UI delegate plugin (CppPluginSystemUIDelegatePlugin).";
      }
      return std::nullopt;
    }};

}  // namespace

CppPluginSystemUIDelegateImplementationFactoryPtr
CppPluginSystemUIDelegateImplementationFactory::make(Str paths, log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemUIDelegateImplementationFactory>(
      CppPluginSystemUIDelegateImplementationFactory{std::move(paths), std::move(logger)});
}

CppPluginSystemUIDelegateImplementationFactoryPtr
CppPluginSystemUIDelegateImplementationFactory::make(log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemUIDelegateImplementationFactory>(
      CppPluginSystemUIDelegateImplementationFactory{std::move(logger)});
}

CppPluginSystemUIDelegateImplementationFactory::CppPluginSystemUIDelegateImplementationFactory(
    Str paths, log::LoggerInterfacePtr logger)
    : UIDelegateImplementationFactoryInterface{std::move(logger)}, paths_{std::move(paths)} {}

CppPluginSystemUIDelegateImplementationFactory::CppPluginSystemUIDelegateImplementationFactory(
    log::LoggerInterfacePtr logger)
    : CppPluginSystemUIDelegateImplementationFactory{"", std::move(logger)} {}

Identifiers CppPluginSystemUIDelegateImplementationFactory::identifiers() {
  if (!pluginSystem_) {
    // Lazy load plugins.
    pluginSystem_ = CppPluginSystem::make(logger());
    pluginSystem_->scan(paths_, kPluginEnvVar, kModuleHookName, kCheckIsUIDelegatePlugin);
  }

  return pluginSystem_->identifiers();
}

managerApi::UIDelegateInterfacePtr CppPluginSystemUIDelegateImplementationFactory::instantiate(
    const Identifier& identifier) {
  if (!pluginSystem_) {
    // Lazy load plugins.
    pluginSystem_ = CppPluginSystem::make(logger());
    pluginSystem_->scan(paths_, kPluginEnvVar, kModuleHookName, kCheckIsUIDelegatePlugin);
  }
  const auto& [path, plugin] = pluginSystem_->plugin(identifier);

  // Should definitely be a UI delegate plugin, as validated by
  // `kCheckIsUIDelegatePlugin`. We use the exception-throwing version
  // of dynamic_cast just to be extra safe.
  auto& uiPlugin = dynamic_cast<CppPluginSystemUIDelegatePlugin&>(*plugin);

  return uiPlugin.interface();
}
}  // namespace ui::pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
