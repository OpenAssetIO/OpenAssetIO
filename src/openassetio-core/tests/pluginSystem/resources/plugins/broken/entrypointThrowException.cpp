// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <entrypointthrow-exception-export.h>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

extern "C" {
using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)();

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
PluginFactory openassetioPlugin() { throw std::runtime_error{"Thrown from entrypoint"}; }
}
