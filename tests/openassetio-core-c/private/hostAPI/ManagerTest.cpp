// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/errors.h>
#include <openassetio/c/hostAPI/Manager.h>
#include <openassetio/c/managerAPI/ManagerInterface.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/hostAPI/Manager.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

// Private headers.
#include <handles.hpp>

#include "../StringViewReporting.hpp"

namespace {
constexpr size_t kStringBufferSize = 500;

namespace managerAPI = openassetio::managerAPI;
namespace hostAPI = openassetio::hostAPI;

/**
 * Mock implementation of a ManagerInterface.
 *
 * Used as constructor parameter to the Manager under test.
 */
struct MockManagerInterface : trompeloeil::mock_interface<managerAPI::ManagerInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_CONST_MOCK0(info);
};

// Converter for ManagerInterface <-> C API handle
// TODO(DF): duplicated from Manager.cpp - should it be available from a header?
using ManagerInterfaceHandleConverter =
    openassetio::handles::Converter<managerAPI::ManagerInterfacePtr,
                                    OPENASSETIO_NS(managerAPI_ManagerInterface_h)>;

using ManagerHandleConverter =
    openassetio::handles::Converter<hostAPI::Manager, OPENASSETIO_NS(hostAPI_Manager_h)>;

}  // namespace

SCENARIO("A Manager is constructed and destructed") {
  // Storage for error messages coming from C API functions.
  openassetio::Str errStorage(kStringBufferSize, '\0');
  OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};
  // A mock ManagerInterface whose lifetime is tracked.
  using DeathwatchedMockManagerInterface = trompeloeil::deathwatched<MockManagerInterface>;

  GIVEN("a shared pointer to a ManagerInterface and its C handle") {
    auto* managerInterface = new DeathwatchedMockManagerInterface{};
    // Wrap deathwatched mock ManagerInterface in a SharedPtr.
    managerAPI::ManagerInterfacePtr mockManagerInterfacePtr{managerInterface};
    // Convert the ManagerInterface pointer to a handle.
    auto* mockManagerInterfaceHandle =
        ManagerInterfaceHandleConverter::toHandle(&mockManagerInterfacePtr);

    AND_GIVEN("a Manager constructed using the C API") {
      // C handle for Manager
      OPENASSETIO_NS(hostAPI_Manager_h) managerHandle;
      // Construct Manager through C API.
      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = OPENASSETIO_NS(hostAPI_Manager_ctor)(&actualErrorMsg, &managerHandle,
                                                             mockManagerInterfaceHandle);
      CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));

      AND_GIVEN("the Manager has exclusive ownership of the ManagerInterface shared pointer") {
        // Release test's pointer to ManagerInterface, so it is
        // exclusively owned by the Manager.
        mockManagerInterfacePtr.reset();

        AND_GIVEN("the ManagerInterface expects to be destroyed") {
          // By the time this block exits, the ManagerInterface should
          // be destroyed because we're about to call `dtor`.
          REQUIRE_DESTRUCTION(*managerInterface);

          WHEN("Manager's dtor C API function is called") {
            OPENASSETIO_NS(hostAPI_Manager_dtor)(managerHandle);

            THEN("wrapped ManagerInterface is destroyed") {
              // Asserted by REQUIRE_DESTRUCTION.
            }
          }
        }
      }
    }
  }

  GIVEN("a shared pointer to a ManagerInterface and its C handle") {
    auto* managerInterface = new DeathwatchedMockManagerInterface{};
    // We must have this expectation here to avoid a false positive.
    REQUIRE_DESTRUCTION(*managerInterface);
    // Wrap deathwatched mock ManagerInterface in a SharedPtr.
    managerAPI::ManagerInterfacePtr mockManagerInterfacePtr{managerInterface};
    // Convert the ManagerInterface pointer to a handle.
    auto* mockManagerInterfaceHandle =
        ManagerInterfaceHandleConverter::toHandle(&mockManagerInterfacePtr);

    AND_GIVEN("a Manager constructed using the C API") {
      // C handle for Manager
      OPENASSETIO_NS(hostAPI_Manager_h) managerHandle;
      // Construct Manager through C API.
      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = OPENASSETIO_NS(hostAPI_Manager_ctor)(&actualErrorMsg, &managerHandle,
                                                             mockManagerInterfaceHandle);
      CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));

      WHEN("Manager's dtor C API function is called") {
        OPENASSETIO_NS(hostAPI_Manager_dtor)(managerHandle);

        THEN("wrapped ManagerInterface is not destroyed") {
          // Asserted implicitly by DeathwatchedMockManagerInterface.
        }
      }
    }
  }
}

SCENARIO("A host calls Manager::identifier") {
  GIVEN("a Manager and its C handle") {
    // Create mock ManagerInterface to inject and assert on.
    managerAPI::ManagerInterfacePtr mockManagerInterfacePtr =
        openassetio::makeShared<MockManagerInterface>();
    auto& mockManagerInterface = static_cast<MockManagerInterface&>(*mockManagerInterfacePtr);

    // Create the Manager under test.
    hostAPI::Manager manager{mockManagerInterfacePtr};
    // Create the handle for the Manager under test.
    auto* managerHandle = ManagerHandleConverter::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    // Storage for identifier - set to an initial value so that we can
    // assert that the underlying data was updated (or not).
    const openassetio::Str initialStrValue = "initial string";
    openassetio::Str identifierStorage = initialStrValue;
    identifierStorage.resize(kStringBufferSize, '\0');
    OPENASSETIO_NS(StringView)
    actualIdentifier{identifierStorage.size(), identifierStorage.data(), initialStrValue.size()};

    AND_GIVEN("ManagerInterface::identifier() will succeed") {
      const openassetio::Str expectedIdentifier = "my.id";
      REQUIRE_CALL(mockManagerInterface, identifier()).RETURN(expectedIdentifier);

      WHEN("the Manager C API is queried for the identifier") {
        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code = OPENASSETIO_NS(hostAPI_Manager_identifier)(&actualErrorMsg, &actualIdentifier,
                                                          managerHandle);

        THEN("the returned identifier matches expected identifier") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kOK));
          CHECK(actualIdentifier == expectedIdentifier);
        }
      }
    }

    AND_GIVEN("ManagerInterface::identifier() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, identifier()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the identifier") {
        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code = OPENASSETIO_NS(hostAPI_Manager_identifier)(&actualErrorMsg, &actualIdentifier,
                                                          managerHandle);

        THEN("generic exception error code and message is set and identifier is unmodified") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kException));
          CHECK(actualErrorMsg == expectedErrorMsg);
          CHECK(actualIdentifier == initialStrValue);
        }
      }
    }
  }
}

SCENARIO("A host calls Manager::displayName") {
  GIVEN("a Manager and its C handle") {
    // Create mock ManagerInterface to inject and assert on.
    managerAPI::ManagerInterfacePtr mockManagerInterfacePtr =
        openassetio::makeShared<MockManagerInterface>();
    auto& mockManagerInterface = static_cast<MockManagerInterface&>(*mockManagerInterfacePtr);

    // Create the Manager under test.
    hostAPI::Manager manager{mockManagerInterfacePtr};
    // Create the handle for the Manager under test.
    auto* managerHandle = ManagerHandleConverter::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    // Storage for displayName - set to an initial value so that we can
    // assert that the underlying data was updated (or not).
    const openassetio::Str initialStrValue = "initial string";
    openassetio::Str displayNameStorage = initialStrValue;
    displayNameStorage.resize(kStringBufferSize, '\0');
    OPENASSETIO_NS(StringView)
    actualDisplayName{displayNameStorage.size(), displayNameStorage.data(),
                      initialStrValue.size()};

    AND_GIVEN("ManagerInterface::displayName() will succeed") {
      const openassetio::Str expectedDisplayName = "My Display Name";
      REQUIRE_CALL(mockManagerInterface, displayName()).RETURN(expectedDisplayName);

      WHEN("the Manager C API is queried for the displayName") {
        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code = OPENASSETIO_NS(hostAPI_Manager_displayName)(&actualErrorMsg, &actualDisplayName,
                                                           managerHandle);

        THEN("the returned displayName matches expected displayName") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kOK));
          CHECK(actualDisplayName == expectedDisplayName);
        }
      }
    }

    AND_GIVEN("ManagerInterface::displayName() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, displayName()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the displayName") {
        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code = OPENASSETIO_NS(hostAPI_Manager_displayName)(&actualErrorMsg, &actualDisplayName,
                                                           managerHandle);

        THEN("generic exception error code and message is set and displayName is unmodified") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kException));
          CHECK(actualErrorMsg == expectedErrorMsg);
          CHECK(actualDisplayName == initialStrValue);
        }
      }
    }
  }
}

SCENARIO("A host calls Manager::info") {
  using InfoDictHandleConverter =
      openassetio::handles::Converter<openassetio::InfoDictionary,
                                      OPENASSETIO_NS(InfoDictionary_h)>;
  GIVEN("a Manager and its C handle") {
    // Create mock ManagerInterface to inject and assert on.
    managerAPI::ManagerInterfacePtr mockManagerInterfacePtr =
        openassetio::makeShared<MockManagerInterface>();
    auto& mockManagerInterface = static_cast<MockManagerInterface&>(*mockManagerInterfacePtr);

    // Create the Manager under test.
    hostAPI::Manager manager{mockManagerInterfacePtr};
    // Create the handle for the Manager under test.
    auto* managerHandle = ManagerHandleConverter::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    // Storage for info - pre-populate so we can assert that calls are
    // destructive (or not).
    const openassetio::InfoDictionary initialInfo{
        {"initial key", openassetio::Str{"initial value"}}};
    openassetio::InfoDictionary actualInfo = initialInfo;

    AND_GIVEN("ManagerInterface::info() will succeed") {
      const openassetio::InfoDictionary expectedInfo{{
          {"a key", openassetio::Int{123}},
      }};
      REQUIRE_CALL(mockManagerInterface, info()).RETURN(expectedInfo);

      WHEN("the Manager C API is queried for the info") {
        OPENASSETIO_NS(InfoDictionary_h)
        actualInfoHandle = InfoDictHandleConverter::toHandle(&actualInfo);

        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code =
            OPENASSETIO_NS(hostAPI_Manager_info)(&actualErrorMsg, actualInfoHandle, managerHandle);

        THEN("the returned info matches expected info") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kOK));
          CHECK(actualInfo == expectedInfo);
        }
      }
    }

    AND_GIVEN("ManagerInterface::info() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, info()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the info") {
        OPENASSETIO_NS(InfoDictionary_h)
        actualInfoHandle = InfoDictHandleConverter::toHandle(&actualInfo);

        // C API call.
        OPENASSETIO_NS(ErrorCode)
        code =
            OPENASSETIO_NS(hostAPI_Manager_info)(&actualErrorMsg, actualInfoHandle, managerHandle);

        THEN("generic exception error code and message is set and info is unmodified") {
          CHECK(code == OPENASSETIO_NS(ErrorCode_kException));
          CHECK(actualErrorMsg == expectedErrorMsg);
          CHECK(actualInfo == initialInfo);
        }
      }
    }
  }
}
