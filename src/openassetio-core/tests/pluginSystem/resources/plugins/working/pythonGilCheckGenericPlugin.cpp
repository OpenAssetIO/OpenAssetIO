// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <memory>

#include <export.h>

#include <Python.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

struct Plugin : openassetio::pluginSystem::CppPluginSystemPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when identifying C++ plugin"};
    }
    return "org.openassetio.test.pluginSystem."
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
}
