// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
// #include <openassetio_test/export.h>
#include <memory>

#include <export.h>

#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "../MockManagerInterface.hpp"

struct Plugin : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    return "org.openassetio.test.pluginSystem.resources.pathA";
  }

  [[nodiscard]] openassetio::managerApi::ManagerInterfacePtr interface() override {
    auto managerInterface = std::make_shared<MockManagerInterface>();
    ALLOW_CALL(*managerInterface, identifier()).RETURN(identifier());
    return managerInterface;
  }
};

OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PATHA_EXPORT
openassetio::pluginSystem::CppPluginSystemManagerPluginPtr openassetioPlugin() {
  return std::make_shared<Plugin>();
}
