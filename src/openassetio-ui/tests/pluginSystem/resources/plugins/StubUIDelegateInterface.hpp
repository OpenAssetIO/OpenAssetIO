// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

struct StubUIDelegateInterface : openassetio::ui::managerApi::UIDelegateInterface {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return "org.openassetio.test.pluginSystem."
           "resources." OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX;
  }

  [[nodiscard]] openassetio::Str displayName() const override { return "Stub UI Delegate"; }

  // Deliberately throw an exception, for use in checking RTTI.
  openassetio::InfoDictionary info() override {
    throw openassetio::errors::NotImplementedException{"Stub doesn't support info"};
  }
};
