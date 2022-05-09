// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

// private headers
#include <handles.hpp>
#include <managerAPI/CManagerInterface.hpp>

#include "MockManagerInterfaceSuite.hpp"

namespace {
// Duplicated from CManagerInterface.
constexpr size_t kStringBufferSize = 500;

using openassetio::test::MockManagerInterfaceCApi;
using openassetio::test::MockManagerInterfaceCApiHandleConverter;
using openassetio::test::mockManagerInterfaceSuite;
}  // namespace

SCENARIO("A CManagerInterface is destroyed") {
  GIVEN("An opaque handle and function suite") {
    MockManagerInterfaceCApi cApi;

    auto *handle = MockManagerInterfaceCApiHandleConverter::toHandle(&cApi);
    auto const suite = mockManagerInterfaceSuite();

    THEN("CManagerInterface's destructor calls the suite's dtor") {
      REQUIRE_CALL(cApi, dtor(handle));

      openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};
    }
  }
}

SCENARIO("A host calls CManagerInterface::identifier") {
  GIVEN("A CManagerInterface wrapping an opaque handle and function suite") {
    MockManagerInterfaceCApi cApi;

    auto *handle = MockManagerInterfaceCApiHandleConverter::toHandle(&cApi);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    // Mysteriously, this must come _before_ the construction
    // of cManagerInterface...
    REQUIRE_CALL(cApi, dtor(handle));

    openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's identifier() call succeeds") {
      const std::string_view expectedIdentifier = "my.id";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update
      // out-parameter.
      REQUIRE_CALL(cApi, identifier(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->capacity == kStringBufferSize)
          // Update StringView out-parameter.
          .LR_SIDE_EFFECT(strncpy(_2->data, expectedIdentifier.data(), expectedIdentifier.size()))
          .LR_SIDE_EFFECT(_2->size = expectedIdentifier.size())
          // Return OK code.
          .RETURN(OPENASSETIO_NS(ErrorCode_kOK));

      WHEN("the manager's identifier is queried") {
        const openassetio::Str actualIdentifier = cManagerInterface.identifier();

        THEN("the returned identifier matches expected identifier") {
          CHECK(actualIdentifier == expectedIdentifier);
        }
      }
    }

    AND_GIVEN("the C suite's identifier() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const auto expectedErrorCode = OPENASSETIO_NS(ErrorCode_kUnknown);
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(cApi, identifier(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_1->capacity == kStringBufferSize)
          // Update StringView error message out-parameter.
          .LR_SIDE_EFFECT(strncpy(_1->data, expectedErrorMsg.data(), expectedErrorMsg.size()))
          .LR_SIDE_EFFECT(_1->size = expectedErrorMsg.size())
          // Return OK code.
          .RETURN(expectedErrorCode);

      WHEN("the manager's identifier is queried") {
        THEN("an exception is thrown with expected error message") {
          REQUIRE_THROWS_MATCHES(cManagerInterface.identifier(), std::runtime_error,
                                 Catch::Message(expectedErrorCodeAndMsg));
        }
      }
    }
  }
}

SCENARIO("A host calls CManagerInterface::displayName") {
  GIVEN("A CManagerInterface wrapping an opaque handle and function suite") {
    MockManagerInterfaceCApi cApi;

    auto *handle = MockManagerInterfaceCApiHandleConverter::toHandle(&cApi);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    REQUIRE_CALL(cApi, dtor(handle));

    openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's displayName() call succeeds") {
      const std::string_view expectedDisplayName = "My Display Name";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update
      // out-parameter.
      REQUIRE_CALL(cApi, displayName(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->capacity == kStringBufferSize)
          // Update StringView out-parameter.
          .LR_SIDE_EFFECT(
              strncpy(_2->data, expectedDisplayName.data(), expectedDisplayName.size()))
          .LR_SIDE_EFFECT(_2->size = expectedDisplayName.size())
          // Return OK code.
          .RETURN(OPENASSETIO_NS(ErrorCode_kOK));

      WHEN("the manager's displayName is queried") {
        const openassetio::Str actualDisplayName = cManagerInterface.displayName();

        THEN("the returned displayName matches expected displayName") {
          CHECK(actualDisplayName == expectedDisplayName);
        }
      }
    }

    AND_GIVEN("the C suite's displayName() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const auto expectedErrorCode = OPENASSETIO_NS(ErrorCode_kUnknown);
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(cApi, displayName(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_1->capacity == kStringBufferSize)
          // Update StringView error message out-parameter.
          .LR_SIDE_EFFECT(strncpy(_1->data, expectedErrorMsg.data(), expectedErrorMsg.size()))
          .LR_SIDE_EFFECT(_1->size = expectedErrorMsg.size())
          // Return OK code.
          .RETURN(expectedErrorCode);

      WHEN("the manager's displayName is queried") {
        THEN("an exception is thrown with expected error message") {
          REQUIRE_THROWS_MATCHES(cManagerInterface.displayName(), std::runtime_error,
                                 Catch::Message(expectedErrorCodeAndMsg));
        }
      }
    }
  }
}

SCENARIO("A host calls CManagerInterface::info") {
  GIVEN("A CManagerInterface wrapping an opaque handle and function suite") {
    MockManagerInterfaceCApi cApi;

    auto *handle = MockManagerInterfaceCApiHandleConverter::toHandle(&cApi);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    REQUIRE_CALL(cApi, dtor(handle));

    openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's info() call succeeds") {
      const openassetio::Str expectedInfoKey = "info key";
      const openassetio::Float expectedInfoValue = 123.456;

      using trompeloeil::_;

      using InfoDictHandleConverter =
          openassetio::handles::Converter<openassetio::InfoDictionary,
                                          OPENASSETIO_NS(InfoDictionary_h)>;

      REQUIRE_CALL(cApi, info(_, _, handle))
          // Update out-parameter.
          .LR_SIDE_EFFECT(InfoDictHandleConverter::toInstance(_2)->insert(
              {expectedInfoKey, expectedInfoValue}))
          // Return OK code.
          .RETURN(OPENASSETIO_NS(ErrorCode_kOK));

      WHEN("the manager's info is queried") {
        const openassetio::InfoDictionary infoDict = cManagerInterface.info();

        THEN("the returned info contains the expected entry") {
          const auto actualInfoValue = std::get<openassetio::Float>(infoDict.at(expectedInfoKey));
          CHECK(actualInfoValue == expectedInfoValue);
        }
      }
    }

    AND_GIVEN("the C suite's info() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const auto expectedErrorCode = OPENASSETIO_NS(ErrorCode_kUnknown);
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `info` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(cApi, info(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_1->capacity == kStringBufferSize)
          // Update StringView error message out-parameter.
          .LR_SIDE_EFFECT(strncpy(_1->data, expectedErrorMsg.data(), expectedErrorMsg.size()))
          .LR_SIDE_EFFECT(_1->size = expectedErrorMsg.size())
          // Return OK code.
          .RETURN(expectedErrorCode);

      WHEN("the manager's info is queried") {
        THEN("an exception is thrown with expected error message") {
          REQUIRE_THROWS_MATCHES(cManagerInterface.info(), std::runtime_error,
                                 Catch::Message(expectedErrorCodeAndMsg));
        }
      }
    }
  }
}
