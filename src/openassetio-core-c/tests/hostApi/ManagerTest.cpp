// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <cstddef>
#include <memory>

#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/hostApi/Manager.h>
#include <openassetio/c/managerApi/HostSession.h>
#include <openassetio/c/managerApi/ManagerInterface.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

// Private headers.
#include <handles/InfoDictionary.hpp>
#include <handles/hostApi/Manager.hpp>
#include <handles/managerApi/HostSession.hpp>
#include <handles/managerApi/ManagerInterface.hpp>

#include "../StringViewReporting.hpp"

namespace managerApi = openassetio::managerApi;
namespace hostApi = openassetio::hostApi;
namespace handles = openassetio::handles;

using openassetio::log::LoggerInterface;
using openassetio::log::LoggerInterfacePtr;

namespace {
constexpr std::size_t kStringBufferSize = 500;
/**
 * Mock implementation of a ManagerInterface.
 *
 * Used as constructor parameter to the Manager under test.
 */
struct MockManagerInterface : trompeloeil::mock_interface<managerApi::ManagerInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK0(info);
  IMPLEMENT_MOCK1(hasCapability);
  IMPLEMENT_MOCK2(initialize);
  IMPLEMENT_MOCK4(managementPolicy);
  IMPLEMENT_MOCK2(isEntityReferenceString);
  IMPLEMENT_MOCK5(entityExists);
  IMPLEMENT_MOCK7(resolve);
  IMPLEMENT_MOCK7(preflight);
  IMPLEMENT_MOCK7(register_);  // NOLINT(readability-identifier-naming)
};
/**
 * Mock implementation of a HostInterface.
 *
 * Used as constructor parameter to Host classes required as part of these tests
 */
struct MockHostInterface : trompeloeil::mock_interface<hostApi::HostInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK0(info);
};
/**
 * Mock implementation of a LoggerInterface
 *
 * Used as constructor parameter to Host classes required as part of these tests
 */
struct MockLoggerInterface : trompeloeil::mock_interface<LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};
}  // namespace

SCENARIO("A Manager is constructed and destructed") {
  // Storage for error messages coming from C API functions.
  openassetio::Str errStorage(kStringBufferSize, '\0');
  oa_StringView actualErrorMsg{errStorage.size(), errStorage.data(), 0};
  // A mock ManagerInterface whose lifetime is tracked.
  using DeathwatchedMockManagerInterface = trompeloeil::deathwatched<MockManagerInterface>;
  using DeathwatchedMockHostInterface = trompeloeil::deathwatched<MockHostInterface>;
  using DeathwatchedMockLoggerInterface = trompeloeil::deathwatched<MockLoggerInterface>;

  GIVEN("a shared pointer to a HostSession and its C handle") {
    auto* hostInterface = new DeathwatchedMockHostInterface{};
    auto* logger = new DeathwatchedMockLoggerInterface{};
    auto hostSessionPtr = managerApi::HostSession::make(
        managerApi::Host::make(hostApi::HostInterfacePtr{hostInterface}),
        LoggerInterfacePtr{logger});
    oa_managerApi_SharedHostSession_h hostSessionHandle =
        handles::managerApi::SharedHostSession::toHandle(&hostSessionPtr);

    AND_GIVEN("a shared pointer to a ManagerInterface and its C handle") {
      auto* managerInterface = new DeathwatchedMockManagerInterface{};
      // Wrap deathwatched mock ManagerInterface in a std::shared_ptr.
      managerApi::ManagerInterfacePtr mockManagerInterfacePtr{managerInterface};
      // Convert the ManagerInterface pointer to a handle.
      oa_managerApi_SharedManagerInterface_h mockManagerInterfaceHandle =
          handles::managerApi::SharedManagerInterface::toHandle(&mockManagerInterfacePtr);

      AND_GIVEN("a Manager constructed using the C API") {
        // C handle for Manager
        oa_hostApi_Manager_h managerHandle = nullptr;
        // Construct Manager through C API.
        const oa_ErrorCode actualErrorCode = oa_hostApi_Manager_ctor(
            &actualErrorMsg, &managerHandle, mockManagerInterfaceHandle, hostSessionHandle);
        CHECK(actualErrorCode == oa_ErrorCode_kOK);

        AND_GIVEN(
            "the Manager has exclusive ownership of the ManagerInterface and HostSession shared "
            "pointers") {
          // Release test's pointer to ManagerInterface/HostInterface
          // and HostSession so it is exclusively owned by the Manager.
          mockManagerInterfacePtr.reset();
          hostSessionPtr.reset();

          AND_GIVEN(
              "the ManagerInterface, HostInterface and LoggerInterface expect to be destroyed") {
            // By the time this block exits, the ManagerInterface and
            // HostInterface should be destroyed because we're about to
            // call `dtor`.
            REQUIRE_DESTRUCTION(*managerInterface);
            REQUIRE_DESTRUCTION(*hostInterface);
            REQUIRE_DESTRUCTION(*logger);

            WHEN("Manager's dtor C API function is called") {
              oa_hostApi_Manager_dtor(managerHandle);

              THEN(
                  "wrapped ManagerInterface, HostInterface and LoggerInterface have been "
                  "destroyed") {
                // Asserted by REQUIRE_DESTRUCTION.
              }
            }
          }
        }
      }
    }
  }

  GIVEN("a shared pointer to a HostSession and its C handle") {
    auto* hostInterface = new DeathwatchedMockHostInterface{};
    auto* logger = new DeathwatchedMockLoggerInterface{};
    // We must have this expectation here to avoid a false positive.
    REQUIRE_DESTRUCTION(*hostInterface);
    REQUIRE_DESTRUCTION(*logger);
    auto hostSessionPtr = managerApi::HostSession::make(
        managerApi::Host::make(hostApi::HostInterfacePtr(hostInterface)),
        LoggerInterfacePtr{logger});
    oa_managerApi_SharedHostSession_h hostSessionHandle =
        handles::managerApi::SharedHostSession::toHandle(&hostSessionPtr);

    AND_GIVEN("a shared pointer to a ManagerInterface and its C handle") {
      auto* managerInterface = new DeathwatchedMockManagerInterface{};
      // We must have this expectation here to avoid a false positive.
      REQUIRE_DESTRUCTION(*managerInterface);
      // Wrap deathwatched mock ManagerInterface in a std::shared_ptr.
      managerApi::ManagerInterfacePtr mockManagerInterfacePtr{managerInterface};
      // Convert the ManagerInterface pointer to a handle.
      oa_managerApi_SharedManagerInterface_h mockManagerInterfaceHandle =
          handles::managerApi::SharedManagerInterface::toHandle(&mockManagerInterfacePtr);

      AND_GIVEN("a Manager constructed using the C API") {
        // C handle for Manager
        oa_hostApi_Manager_h managerHandle = nullptr;
        // Construct Manager through C API.
        const oa_ErrorCode actualErrorCode = oa_hostApi_Manager_ctor(
            &actualErrorMsg, &managerHandle, mockManagerInterfaceHandle, hostSessionHandle);
        CHECK(actualErrorCode == oa_ErrorCode_kOK);

        WHEN("Manager's dtor C API function is called") {
          oa_hostApi_Manager_dtor(managerHandle);

          THEN("wrapped ManagerInterface, HostInterface and LoggerInterface are not destroyed") {
            // Asserted implicitly by DeathwatchedMockManagerInterface.
            // Asserted implicitly by DeathwatchedMockHostInterface.
            // Asserted implicitly by DeathwatchedMockLoggerInterface.
          }
        }
      }
    }
  }
}

SCENARIO("A host calls Manager::identifier") {
  GIVEN("a Manager and its C handle") {
    // Create mock ManagerInterface to inject and assert on.
    const managerApi::ManagerInterfacePtr mockManagerInterfacePtr =
        std::make_shared<MockManagerInterface>();
    auto& mockManagerInterface = dynamic_cast<MockManagerInterface&>(*mockManagerInterfacePtr);
    // Create a HostSession with our mock HostInterface
    const managerApi::HostSessionPtr hostSessionPtr = managerApi::HostSession::make(
        managerApi::Host::make(std::make_shared<MockHostInterface>()),
        std::make_shared<MockLoggerInterface>());

    // Create the Manager under test.
    hostApi::ManagerPtr manager = hostApi::Manager::make(mockManagerInterfacePtr, hostSessionPtr);
    // Create the handle for the Manager under test.
    oa_hostApi_Manager_h managerHandle = handles::hostApi::SharedManager::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    oa_StringView actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    // Storage for identifier - set to an initial value so that we can
    // assert that the underlying data was updated (or not).
    const openassetio::Str initialStrValue = "initial string";
    openassetio::Str identifierStorage = initialStrValue;
    identifierStorage.resize(kStringBufferSize, '\0');
    oa_StringView actualIdentifier{identifierStorage.size(), identifierStorage.data(),
                                   initialStrValue.size()};

    AND_GIVEN("ManagerInterface::identifier() will succeed") {
      const openassetio::Identifier expectedIdentifier = "my.id";
      REQUIRE_CALL(mockManagerInterface, identifier()).RETURN(expectedIdentifier);

      WHEN("the Manager C API is queried for the identifier") {
        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_identifier(&actualErrorMsg, &actualIdentifier, managerHandle);

        THEN("the returned identifier matches expected identifier") {
          CHECK(code == oa_ErrorCode_kOK);
          CHECK(actualIdentifier == expectedIdentifier);
        }
      }
    }

    AND_GIVEN("ManagerInterface::identifier() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, identifier()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the identifier") {
        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_identifier(&actualErrorMsg, &actualIdentifier, managerHandle);

        THEN("generic exception error code and message is set and identifier is unmodified") {
          CHECK(code == oa_ErrorCode_kException);
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
    const managerApi::ManagerInterfacePtr mockManagerInterfacePtr =
        std::make_shared<MockManagerInterface>();
    auto& mockManagerInterface = dynamic_cast<MockManagerInterface&>(*mockManagerInterfacePtr);
    // Create a HostSession with our mock HostInterface
    const managerApi::HostSessionPtr hostSessionPtr = managerApi::HostSession::make(
        managerApi::Host::make(std::make_shared<MockHostInterface>()),
        std::make_shared<MockLoggerInterface>());

    // Create the Manager under test.
    hostApi::ManagerPtr manager = hostApi::Manager::make(mockManagerInterfacePtr, hostSessionPtr);
    // Create the handle for the Manager under test.
    oa_hostApi_Manager_h managerHandle = handles::hostApi::SharedManager::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    oa_StringView actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    // Storage for displayName - set to an initial value so that we can
    // assert that the underlying data was updated (or not).
    const openassetio::Str initialStrValue = "initial string";
    openassetio::Str displayNameStorage = initialStrValue;
    displayNameStorage.resize(kStringBufferSize, '\0');
    oa_StringView actualDisplayName{displayNameStorage.size(), displayNameStorage.data(),
                                    initialStrValue.size()};

    AND_GIVEN("ManagerInterface::displayName() will succeed") {
      const openassetio::Str expectedDisplayName = "My Display Name";
      REQUIRE_CALL(mockManagerInterface, displayName()).RETURN(expectedDisplayName);

      WHEN("the Manager C API is queried for the displayName") {
        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_displayName(&actualErrorMsg, &actualDisplayName, managerHandle);

        THEN("the returned displayName matches expected displayName") {
          CHECK(code == oa_ErrorCode_kOK);
          CHECK(actualDisplayName == expectedDisplayName);
        }
      }
    }

    AND_GIVEN("ManagerInterface::displayName() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, displayName()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the displayName") {
        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_displayName(&actualErrorMsg, &actualDisplayName, managerHandle);

        THEN("generic exception error code and message is set and displayName is unmodified") {
          CHECK(code == oa_ErrorCode_kException);
          CHECK(actualErrorMsg == expectedErrorMsg);
          CHECK(actualDisplayName == initialStrValue);
        }
      }
    }
  }
}

SCENARIO("A host calls Manager::info") {
  GIVEN("a Manager and its C handle") {
    // Create mock ManagerInterface to inject and assert on.
    const managerApi::ManagerInterfacePtr mockManagerInterfacePtr =
        std::make_shared<MockManagerInterface>();
    auto& mockManagerInterface = dynamic_cast<MockManagerInterface&>(*mockManagerInterfacePtr);
    // Create a HostSession with our mock HostInterface
    const managerApi::HostSessionPtr hostSessionPtr = managerApi::HostSession::make(
        managerApi::Host::make(std::make_shared<MockHostInterface>()),
        std::make_shared<MockLoggerInterface>());

    // Create the Manager under test.
    hostApi::ManagerPtr manager = hostApi::Manager::make(mockManagerInterfacePtr, hostSessionPtr);
    // Create the handle for the Manager under test.
    oa_hostApi_Manager_h managerHandle = handles::hostApi::SharedManager::toHandle(&manager);

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStringBufferSize, '\0');
    oa_StringView actualErrorMsg{errStorage.size(), errStorage.data(), 0};

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
        oa_InfoDictionary_h actualInfoHandle = handles::InfoDictionary::toHandle(&actualInfo);

        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_info(&actualErrorMsg, actualInfoHandle, managerHandle);

        THEN("the returned info matches expected info") {
          CHECK(code == oa_ErrorCode_kOK);
          CHECK(actualInfo == expectedInfo);
        }
      }
    }

    AND_GIVEN("ManagerInterface::info() will fail with an exception") {
      const openassetio::Str expectedErrorMsg = "Some error";
      REQUIRE_CALL(mockManagerInterface, info()).THROW(std::logic_error{expectedErrorMsg});

      WHEN("the Manager C API is queried for the info") {
        oa_InfoDictionary_h actualInfoHandle = handles::InfoDictionary::toHandle(&actualInfo);

        // C API call.
        const oa_ErrorCode code =
            oa_hostApi_Manager_info(&actualErrorMsg, actualInfoHandle, managerHandle);

        THEN("generic exception error code and message is set and info is unmodified") {
          CHECK(code == oa_ErrorCode_kException);
          CHECK(actualErrorMsg == expectedErrorMsg);
          CHECK(actualInfo == initialInfo);
        }
      }
    }
  }
}
