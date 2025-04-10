// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <memory>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>

namespace {
/**
 * Mock implementation of a LoggerInterface
 */
struct MockLoggerInterface final : trompeloeil::mock_interface<openassetio::log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};
}  // namespace

SCENARIO("CppPluginSystem::scan") {
  GIVEN("a CppPluginSystem") {
    auto logger = std::make_shared<MockLoggerInterface>();
    auto cppPluginSystem = openassetio::pluginSystem::CppPluginSystem::make(logger);

    using trompeloeil::_;
    ALLOW_CALL(*logger, log(_, _));

    WHEN("scan() called with uninitialised arguments") {
      cppPluginSystem->scan({}, {}, {}, {});

      THEN("no segfault") { CHECK(cppPluginSystem->identifiers().empty()); }
    }
  }
}
