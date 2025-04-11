// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include <memory>

#include <export.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include "openassetio/typedefs.hpp"

struct Plugin : openassetio::pluginSystem::CppPluginSystemPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    return "org.openassetio.test.pluginSystem."
           // NOLINTNEXTLINE(misc-include-cleaner) - definition provided on command line.
           "resources." OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }
};

extern "C" {

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::PluginFactory openassetioPlugin() noexcept {
  return []() noexcept -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<Plugin>();
  };
}

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::PluginFactory openassetioUIPlugin() noexcept {
  return []() noexcept -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<Plugin>();
  };
}
}
