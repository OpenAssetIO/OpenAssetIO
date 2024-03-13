// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <entrypointthrow-exception-export.h>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

extern "C" {
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
#endif
OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::CppPluginSystemPluginPtr openassetioPlugin() {
  throw std::runtime_error{"Thrown from entrypoint"};
}
}
