// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
// #include <openassetio_test/export.h>
#include <memory>

#include <export.h>

#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "MockManagerInterface.hpp"

struct Plugin : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    return "org.openassetio.test.pluginSystem."
           "resources." OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }

  [[nodiscard]] openassetio::managerApi::ManagerInterfacePtr interface() override {
    auto managerInterface = std::make_shared<MockManagerInterface>();
    ALLOW_CALL(*managerInterface, identifier()).RETURN(identifier());
    ALLOW_CALL(*managerInterface, info())
        .RETURN(openassetio::InfoDictionary{
            {"path_suffix", OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_PATH_SUFFIX}});
    return managerInterface;
  }
};

extern "C" {
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
#endif

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
openassetio::pluginSystem::CppPluginSystemPluginPtr openassetioPlugin() {
  return std::make_shared<Plugin>();
}
}
