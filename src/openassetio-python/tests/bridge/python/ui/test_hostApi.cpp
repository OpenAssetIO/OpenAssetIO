// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <memory>

#include <pybind11/pybind11.h>
#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/python/ui/hostApi.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>

namespace {
struct MockLogger : trompeloeil::mock_interface<openassetio::log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};
using trompeloeil::_;
}  // namespace

SCENARIO("Accessing the Python UI delegate plugin system from C++") {
  GIVEN("a logger") {
    // Release the GIL to ensure GIL-safe handling of Python import.
    const pybind11::gil_scoped_release gil{};

    const openassetio::log::LoggerInterfacePtr logger = std::make_shared<MockLogger>();
    auto& mockLogger = dynamic_cast<MockLogger&>(*logger);

    ALLOW_CALL(mockLogger, log(_, _));

    AND_GIVEN("a Python plugin system UI delegate factory") {
      const openassetio::ui::hostApi::UIDelegateImplementationFactoryInterfacePtr factory =
          openassetio::python::ui::hostApi::
              createPythonPluginSystemUIDelegateImplementationFactory(logger);

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
