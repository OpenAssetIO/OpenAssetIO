// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <identifierthrow-exception-export.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

class ThrowingPlugin : public openassetio::pluginSystem::CppPluginSystemPlugin {
 public:
  [[nodiscard]] openassetio::Str identifier() const override {
    throw openassetio::errors::NotImplementedException{"Thrown from identifier"};
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
