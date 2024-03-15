// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
// #include <openassetio_test/export.h>
#include <memory>

#include <export.h>

#include <Python.h>

#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "../MockManagerInterface.hpp"

struct Plugin : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when identifying C++ plugin"};
    }
    return "org.openassetio.test.pluginSystem.python.gil-check";
  }
  openassetio::managerApi::ManagerInterfacePtr interface() override {
    if (PyGILState_Check()) {
      throw std::runtime_error{"GIL was not released when instantiating C++ plugin"};
    }
    return std::make_shared<MockManagerInterface>();
  }
};

extern "C" {
using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)();

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
PluginFactory openassetioPlugin() {
  if (PyGILState_Check()) {
    throw std::runtime_error{"GIL was not released when loading C++ plugin"};
  }
  return []() -> openassetio::pluginSystem::CppPluginSystemPluginPtr {
    return std::make_shared<Plugin>();
  };
}
}
