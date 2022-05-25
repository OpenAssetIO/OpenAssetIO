// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

// private headers
#include <handles/InfoDictionary.hpp>
#include <managerAPI/CManagerInterfaceAdapter.hpp>

#include "MockManagerInterfaceSuite.hpp"

namespace {
// Duplicated from CManagerInterfaceAdapter.
constexpr size_t kStringBufferSize = 500;
}  // namespace

namespace handles = openassetio::handles;
using openassetio::test::MockCManagerInterfaceHandleConverter;
using openassetio::test::MockCManagerInterfaceImpl;
using openassetio::test::mockManagerInterfaceSuite;

SCENARIO("A CManagerInterfaceAdapter is destroyed") {
  GIVEN("An opaque handle and function suite") {
    MockCManagerInterfaceImpl mockImpl;

    auto *handle = MockCManagerInterfaceHandleConverter::toHandle(&mockImpl);
    auto const suite = mockManagerInterfaceSuite();

    THEN("CManagerInterfaceAdapter's destructor calls the suite's dtor") {
      REQUIRE_CALL(mockImpl, dtor(handle));

      openassetio::managerAPI::CManagerInterfaceAdapter cManagerInterface{handle, suite};
    }
  }
}

SCENARIO("A host calls CManagerInterfaceAdapter::identifier") {
  GIVEN("A CManagerInterfaceAdapter wrapping an opaque handle and function suite") {
    MockCManagerInterfaceImpl mockImpl;

    auto *handle = MockCManagerInterfaceHandleConverter::toHandle(&mockImpl);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    // Mysteriously, this must come _before_ the construction
    // of cManagerInterface...
    REQUIRE_CALL(mockImpl, dtor(handle));

    openassetio::managerAPI::CManagerInterfaceAdapter cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's identifier() call succeeds") {
      const std::string_view expectedIdentifier = "my.id";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update
      // out-parameter.
      REQUIRE_CALL(mockImpl, identifier(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->capacity == kStringBufferSize)
          // Update StringView out-parameter.
          .LR_SIDE_EFFECT(strncpy(_2->data, expectedIdentifier.data(), expectedIdentifier.size()))
          .LR_SIDE_EFFECT(_2->size = expectedIdentifier.size())
          // Return OK code.
          .RETURN(oa_ErrorCode_kOK);

      WHEN("the manager's identifier is queried") {
        const openassetio::Str actualIdentifier = cManagerInterface.identifier();

        THEN("the returned identifier matches expected identifier") {
          CHECK(actualIdentifier == expectedIdentifier);
        }
      }
    }

    AND_GIVEN("the C suite's identifier() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const auto expectedErrorCode = oa_ErrorCode_kUnknown;
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(mockImpl, identifier(_, _, handle))
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

SCENARIO("A host calls CManagerInterfaceAdapter::displayName") {
  GIVEN("A CManagerInterfaceAdapter wrapping an opaque handle and function suite") {
    MockCManagerInterfaceImpl mockImpl;

    auto *handle = MockCManagerInterfaceHandleConverter::toHandle(&mockImpl);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    REQUIRE_CALL(mockImpl, dtor(handle));

    openassetio::managerAPI::CManagerInterfaceAdapter cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's displayName() call succeeds") {
      const std::string_view expectedDisplayName = "My Display Name";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update
      // out-parameter.
      REQUIRE_CALL(mockImpl, displayName(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->capacity == kStringBufferSize)
          // Update StringView out-parameter.
          .LR_SIDE_EFFECT(
              strncpy(_2->data, expectedDisplayName.data(), expectedDisplayName.size()))
          .LR_SIDE_EFFECT(_2->size = expectedDisplayName.size())
          // Return OK code.
          .RETURN(oa_ErrorCode_kOK);

      WHEN("the manager's displayName is queried") {
        const openassetio::Str actualDisplayName = cManagerInterface.displayName();

        THEN("the returned displayName matches expected displayName") {
          CHECK(actualDisplayName == expectedDisplayName);
        }
      }
    }

    AND_GIVEN("the C suite's displayName() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const auto expectedErrorCode = oa_ErrorCode_kUnknown;
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(mockImpl, displayName(_, _, handle))
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

SCENARIO("A host calls CManagerInterfaceAdapter::info") {
  GIVEN("A CManagerInterfaceAdapter wrapping an opaque handle and function suite") {
    MockCManagerInterfaceImpl mockImpl;

    auto *handle = MockCManagerInterfaceHandleConverter::toHandle(&mockImpl);
    auto const suite = mockManagerInterfaceSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    REQUIRE_CALL(mockImpl, dtor(handle));

    openassetio::managerAPI::CManagerInterfaceAdapter cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's info() call succeeds") {
      const openassetio::Str expectedInfoKey = "info key";
      const openassetio::Float expectedInfoValue = 123.456;

      using trompeloeil::_;

      REQUIRE_CALL(mockImpl, info(_, _, handle))
          // Update out-parameter.
          .LR_SIDE_EFFECT(handles::InfoDictionary::toInstance(_2)->insert(
              {expectedInfoKey, expectedInfoValue}))
          // Return OK code.
          .RETURN(oa_ErrorCode_kOK);

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
      const auto expectedErrorCode = oa_ErrorCode_kUnknown;
      const openassetio::Str expectedErrorCodeAndMsg = "1: some error happened";

      using trompeloeil::_;

      // Check that `info` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(mockImpl, info(_, _, handle))
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
