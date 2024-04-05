// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>

struct StubManagerInterface : openassetio::managerApi::ManagerInterface {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return "org.openassetio.test.pluginSystem."
           "resources." OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }

  [[nodiscard]] openassetio::Str displayName() const override {
    return OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }

  bool hasCapability([[maybe_unused]] Capability capability) override { return false; }

  // Deliberately throw an exception, for use in checking RTTI.
  openassetio::InfoDictionary info() override {
    throw openassetio::errors::NotImplementedException{"Stub doesn't support info"};
  }
};
