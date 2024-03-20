// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <factory-returnnull-export.h>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)();
extern "C" {
OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
PluginFactory openassetioPlugin() {
  return []() -> openassetio::pluginSystem::CppPluginSystemPluginPtr { return nullptr; };
}
}
