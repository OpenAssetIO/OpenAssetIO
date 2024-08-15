// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd

#include <pybind11/pybind11.h>
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
    // Release the GIL to ensure GIL-safe handling of Python import.
    const pybind11::gil_scoped_release gil{};

    const openassetio::log::LoggerInterfacePtr logger = std::make_shared<MockLogger>();
    auto& mockLogger = static_cast<MockLogger&>(*logger);

    ALLOW_CALL(mockLogger, log(_, _));

    AND_GIVEN("a Python plugin system manager factory") {
      const openassetio::hostApi::ManagerImplementationFactoryInterfacePtr factory =
          openassetio::python::hostApi::createPythonPluginSystemManagerImplementationFactory(
              logger);

      WHEN("the list of plugin identifiers is queried") {
        const openassetio::Identifiers identifiers = factory->identifiers();

        THEN("identifiers list is contains expected entry") {
          // Assumes
          CHECK(identifiers == openassetio::Identifiers{
                                   "org.openassetio.test.pluginSystem.resources.modulePlugin"});
        }
      }
    }
  }
}
