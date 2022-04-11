// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>
// private headers
#include <managerAPI/CManagerInterface.hpp>

// Duplicated from CManagerInterface.
constexpr size_t kStringBufferSize = 500;

/**
 * Mock manager API implementation that the function pointer suite (see
 * `getSuite`) will delegate to.
 */
struct MockCAPI {
  MAKE_MOCK1(dtor, void(OPENASSETIO_NS(managerAPI_ManagerInterface_h)));

  MAKE_MOCK3(identifier, int(OPENASSETIO_NS(SimpleString) *, OPENASSETIO_NS(SimpleString) *,
                             OPENASSETIO_NS(managerAPI_ManagerInterface_h)));

  MAKE_MOCK3(displayName, int(OPENASSETIO_NS(SimpleString) *, OPENASSETIO_NS(SimpleString) *,
                              OPENASSETIO_NS(managerAPI_ManagerInterface_h)));
};

/**
 * Get a ManagerInterface C API function pointer suite that assumes the
 * provided `handle` is a `MockCAPI` instance.
 */
OPENASSETIO_NS(managerAPI_ManagerInterface_s) getSuite() {
  return {// dtor
          [](OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = reinterpret_cast<MockCAPI *>(h);
            api->dtor(h);
          },
          // identifier
          [](OPENASSETIO_NS(SimpleString) * err, OPENASSETIO_NS(SimpleString) * out,
             OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = reinterpret_cast<MockCAPI *>(h);
            return api->identifier(err, out, h);
          },
          // displayName
          [](OPENASSETIO_NS(SimpleString) * err, OPENASSETIO_NS(SimpleString) * out,
             OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = reinterpret_cast<MockCAPI *>(h);
            return api->displayName(err, out, h);
          }};
}

SCENARIO("A CManagerInterface is destroyed") {
  GIVEN("An opaque handle and function suite") {
    MockCAPI capi;

    auto *handle = reinterpret_cast<OPENASSETIO_NS(managerAPI_ManagerInterface_h)>(&capi);
    auto const suite = getSuite();

    THEN("CManagerInterface's destructor calls the suite's dtor") {
      REQUIRE_CALL(capi, dtor(handle));

      openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};
    }
  }
}

SCENARIO("A host calls CManagerInterface::identifier") {
  GIVEN("A CManagerInterface wrapping an opaque handle and function suite") {
    MockCAPI capi;

    auto *handle = reinterpret_cast<OPENASSETIO_NS(managerAPI_ManagerInterface_h)>(&capi);
    auto const suite = getSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    // Mysteriously, this must come _before_ the construction
    // of cManagerInterface...
    REQUIRE_CALL(capi, dtor(handle));

    openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's identifier() call succeeds") {
      const std::string_view expectedIdentifier = "my.id";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update
      // out-parameter.
      REQUIRE_CALL(capi, identifier(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->maxSize == kStringBufferSize)
          // Update SimpleString out-parameter.
          .LR_SIDE_EFFECT(
              strncpy(_2->buffer, expectedIdentifier.data(), expectedIdentifier.size()))
          .LR_SIDE_EFFECT(_2->usedSize = expectedIdentifier.size())
          // Return OK code.
          .RETURN(OPENASSETIO_NS(kOK));

      WHEN("the manager's identifier is queried") {
        const openassetio::Str actualIdentifier = cManagerInterface.identifier();

        THEN("the returned identifier matches expected identifier") {
          CHECK(actualIdentifier == expectedIdentifier);
        }
      }
    }

    AND_GIVEN("the C suite's identifier() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const int expectedErrorCode = 123;
      const openassetio::Str expectedErrorCodeAndMsg = "123: some error happened";

      using trompeloeil::_;

      // Check that `identifier` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(capi, identifier(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_1->maxSize == kStringBufferSize)
          // Update SimpleString error message out-parameter.
          .LR_SIDE_EFFECT(strncpy(_1->buffer, expectedErrorMsg.data(), expectedErrorMsg.size()))
          .LR_SIDE_EFFECT(_1->usedSize = expectedErrorMsg.size())
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
    MockCAPI capi;

    auto *handle = reinterpret_cast<OPENASSETIO_NS(managerAPI_ManagerInterface_h)>(&capi);
    auto const suite = getSuite();

    // Expect the destructor to be called, i.e. when cManagerInterface
    // goes out of scope.
    REQUIRE_CALL(capi, dtor(handle));

    openassetio::managerAPI::CManagerInterface cManagerInterface{handle, suite};

    AND_GIVEN("the C suite's displayName() call succeeds") {
      const std::string_view expectedDisplayName = "My Display Name";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update
      // out-parameter.
      REQUIRE_CALL(capi, displayName(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_2->maxSize == kStringBufferSize)
          // Update SimpleString out-parameter.
          .LR_SIDE_EFFECT(
              strncpy(_2->buffer, expectedDisplayName.data(), expectedDisplayName.size()))
          .LR_SIDE_EFFECT(_2->usedSize = expectedDisplayName.size())
          // Return OK code.
          .RETURN(OPENASSETIO_NS(kOK));

      WHEN("the manager's displayName is queried") {
        const openassetio::Str actualDisplayName = cManagerInterface.displayName();

        THEN("the returned displayName matches expected displayName") {
          CHECK(actualDisplayName == expectedDisplayName);
        }
      }
    }

    AND_GIVEN("the C suite's displayName() call fails") {
      const std::string_view expectedErrorMsg = "some error happened";
      const int expectedErrorCode = 123;
      const openassetio::Str expectedErrorCodeAndMsg = "123: some error happened";

      using trompeloeil::_;

      // Check that `displayName` is called properly and update error
      // message out-parameter.
      REQUIRE_CALL(capi, displayName(_, _, handle))
          // Ensure max size is reasonable.
          .LR_WITH(_1->maxSize == kStringBufferSize)
          // Update SimpleString error message out-parameter.
          .LR_SIDE_EFFECT(strncpy(_1->buffer, expectedErrorMsg.data(), expectedErrorMsg.size()))
          .LR_SIDE_EFFECT(_1->usedSize = expectedErrorMsg.size())
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
