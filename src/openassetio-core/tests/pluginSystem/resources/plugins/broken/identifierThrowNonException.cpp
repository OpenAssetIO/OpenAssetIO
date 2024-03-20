// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <identifierthrow-nonexception-export.h>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

class ThrowingPlugin : public openassetio::pluginSystem::CppPluginSystemPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    throw 123;
  }
};

using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)();
extern "C" {
OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
PluginFactory openassetioPlugin() {
  return []() -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<ThrowingPlugin>();
  };
}
}
