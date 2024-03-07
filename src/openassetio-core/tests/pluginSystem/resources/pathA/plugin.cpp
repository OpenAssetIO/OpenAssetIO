// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
// #include <openassetio_test/export.h>
#include <memory>

#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "../MockManagerInterface.hpp"

struct PathAPluginSystemManagerPlugin : openassetio::pluginSystem::CppPluginSystemManagerPlugin {
  [[nodiscard]] openassetio::Str identifier() const override {
    return "org.openassetio.test.pluginSystem.resources.pathA";
  }

  [[nodiscard]] openassetio::managerApi::ManagerInterfacePtr interface() override {
    return std::make_shared<MockManagerInterface>();
  }
};
