// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <memory>

#include <export.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

class ThrowingPlugin : public openassetio::pluginSystem::CppPluginSystemPlugin {
  [[nodiscard]] openassetio::Str identifier() const override { throw 0; }
};

extern "C" {
OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::PluginFactory openassetioPlugin() noexcept {
  return []() noexcept -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<ThrowingPlugin>();
  };
}
}
