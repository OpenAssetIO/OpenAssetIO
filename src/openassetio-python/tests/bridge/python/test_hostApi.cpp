// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/python/hostApi.hpp>

namespace {
struct MockLogger : trompeloeil::mock_interface<openassetio::log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};
using trompeloeil::_;
}  // namespace

SCENARIO("Accessing the Python plugin system from C++") {
  GIVEN("a logger") {
    openassetio::log::LoggerInterfacePtr logger = std::make_shared<MockLogger>();
    auto& mockLogger = static_cast<MockLogger&>(*logger);

    ALLOW_CALL(mockLogger, log(_, _));

    WHEN("Python plugin system manager factory is created") {
      const auto factory =
          openassetio::python::hostApi::createPythonPluginSystemManagerImplementationFactory(
              logger);

      THEN("identifiers list is contains expected entry") {
        // Assumes
        CHECK(
            factory->identifiers() ==
            openassetio::Identifiers{"org.openassetio.test.pluginSystem.resources.modulePlugin"});
      }
    }
  }
}
