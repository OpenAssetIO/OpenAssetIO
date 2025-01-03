// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <memory>

#include <Python.h>

#include <export.h>

#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "StubManagerInterface.hpp"

struct Plugin : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when identifying C++ plugin"};
    }
    return "org.openassetio.test.pluginSystem.resources."
        // NOLINTNEXTLINE(*-include-cleaner): since defined on command line.
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }
  openassetio::managerApi::ManagerInterfacePtr interface() override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when instantiating manager from C++ plugin"};
    }
    return std::make_shared<StubManagerInterface>();
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
