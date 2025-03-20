// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <memory>
#include <stdexcept>

#include <Python.h>

#include <export.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>
#include <openassetio/ui/pluginSystem/CppPluginSystemUIDelegatePlugin.hpp>

#include "StubUIDelegateInterface.hpp"

struct Plugin : openassetio::ui::pluginSystem::CppPluginSystemUIDelegatePlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when identifying C++ plugin"};
    }
    return "org.openassetio.test.pluginSystem.resources."
        // NOLINTNEXTLINE(*-include-cleaner): since defined on command line.
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }

  openassetio::ui::managerApi::UIDelegateInterfacePtr interface() override {
    if (PyGILState_Check()) {
      throw std::runtime_error{
          "GIL was not released when instantiating UI delegate from C++ plugin"};
    }
    return std::make_shared<StubUIDelegateInterface>();
  }
};

extern "C" {

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::PluginFactory openassetioUIPlugin() noexcept {
  return []() noexcept -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<Plugin>();
  };
}
}
