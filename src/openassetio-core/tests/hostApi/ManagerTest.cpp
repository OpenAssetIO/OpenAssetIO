// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <type_traits>
#include <variant>

#include <openassetio/export.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
// Equality comparison for BatchElementError, useful in tests.
// TODO(DF): implement in main codebase
//  https://github.com/OpenAssetIO/OpenAssetIO/issues/862
bool operator==(const BatchElementError& lhs, const BatchElementError& rhs) {
  return lhs.code == rhs.code && lhs.message == rhs.message;
}

namespace {
/**
 * Mock implementation of a ManagerInterface.
 *
 * Used as constructor parameter to the Manager under test.
 */
struct MockManagerInterface : trompeloeil::mock_interface<managerApi::ManagerInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_CONST_MOCK0(info);
  IMPLEMENT_MOCK2(initialize);
  IMPLEMENT_CONST_MOCK3(managementPolicy);
  IMPLEMENT_CONST_MOCK2(isEntityReferenceString);
  IMPLEMENT_MOCK6(resolve);
  IMPLEMENT_MOCK6(preflight);
  IMPLEMENT_MOCK6(register_);  // NOLINT(readability-identifier-naming)
};
/**
 * Mock implementation of a HostInterface.
 *
 * Used as constructor parameter to Host classes required as part of these tests
 */
struct MockHostInterface : trompeloeil::mock_interface<hostApi::HostInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_CONST_MOCK0(info);
};
/**
 * Mock implementation of a LoggerInterface
 *
 * Used as constructor parameter to Host classes required as part of these tests
 */
struct MockLoggerInterface : trompeloeil::mock_interface<log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};

/**
 * Fixture providing a Manager instance injected with mock dependencies.
 */
struct ManagerFixture {
  const std::shared_ptr<managerApi::ManagerInterface> managerInterface =
      std::make_shared<openassetio::MockManagerInterface>();

  // For convenience, to avoid casting all the time in tests.
  MockManagerInterface& mockManagerInterface =
      static_cast<openassetio::MockManagerInterface&>(*managerInterface);

  // Create a HostSession with our mock HostInterface
  const managerApi::HostSessionPtr hostSession = managerApi::HostSession::make(
      managerApi::Host::make(std::make_shared<openassetio::MockHostInterface>()),
      std::make_shared<openassetio::MockLoggerInterface>());

  // Create the Manager under test.
  const hostApi::ManagerPtr manager = hostApi::Manager::make(managerInterface, hostSession);

  // For convenience, since almost every method takes a Context.
  const openassetio::ContextPtr context{openassetio::Context::make()};
};

}  // namespace
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

SCENARIO("Manager constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<openassetio::hostApi::Manager,
                                               openassetio::managerApi::ManagerInterfacePtr>);
}

SCENARIO("Resolving entities") {
  namespace hostApi = openassetio::hostApi;
  using trompeloeil::_;

  GIVEN("a configured Manager instance") {
    const openassetio::trait::TraitSet traits = {"fakeTrait", "secondFakeTrait"};
    const openassetio::ManagerFixture fixture;
    const auto& manager = fixture.manager;
    auto& mockManagerInterface = fixture.mockManagerInterface;
    const auto& context = fixture.context;
    const auto& hostSession = fixture.hostSession;

    GIVEN("manager plugin successfully resolves a single entity reference") {
      const openassetio::EntityReference ref = openassetio::EntityReference{"testReference"};
      const openassetio::EntityReferences refs = {ref};

      const openassetio::TraitsDataPtr expected = openassetio::TraitsData::make();
      expected->addTrait("aTestTrait");

      // With success callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_5(0, expected));

      WHEN("singular resolve is called with default errorPolicyTag") {
        const openassetio::TraitsDataPtr actual = manager->resolve(ref, traits, context);
        THEN("returned TraitsData is as expected") { CHECK(expected.get() == actual.get()); }
      }
      WHEN("singular resolve is called with kException errorPolicyTag") {
        const openassetio::TraitsDataPtr actual = manager->resolve(
            ref, traits, context, hostApi::Manager::BatchElementErrorPolicyTag::kException);
        THEN("returned TraitsData is as expected") { CHECK(expected.get() == actual.get()); }
      }
      WHEN("singular resolve is called with kVariant errorPolicyTag") {
        std::variant<openassetio::BatchElementError, openassetio::TraitsDataPtr> actual =
            manager->resolve(ref, traits, context,
                             hostApi::Manager::BatchElementErrorPolicyTag::kVariant);
        THEN("returned variant contains the expected TraitsData") {
          CHECK(std::holds_alternative<openassetio::TraitsDataPtr>(actual));
          auto actualVal = std::get<openassetio::TraitsDataPtr>(actual);
          CHECK(expected.get() == actualVal.get());
        }
      }
    }
    GIVEN("manager plugin successfully resolves multiple entity references") {
      const openassetio::EntityReferences refs = {openassetio::EntityReference{"testReference1"},
                                                  openassetio::EntityReference{"testReference2"},
                                                  openassetio::EntityReference{"testReference3"}};

      const openassetio::TraitsDataPtr expected1 = openassetio::TraitsData::make();
      expected1->addTrait("aTestTrait1");
      const openassetio::TraitsDataPtr expected2 = openassetio::TraitsData::make();
      expected2->addTrait("aTestTrait2");
      const openassetio::TraitsDataPtr expected3 = openassetio::TraitsData::make();
      expected3->addTrait("aTestTrait3");
      std::vector<openassetio::TraitsDataPtr> expectedVec{expected1, expected2, expected3};

      // With success callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_5(0, expectedVec[0]))
          .LR_SIDE_EFFECT(_5(1, expectedVec[1]))
          .LR_SIDE_EFFECT(_5(2, expectedVec[2]));

      WHEN("batch resolve is called with default errorPolicyTag") {
        const std::vector<openassetio::TraitsDataPtr> actualVec =
            manager->resolve(refs, traits, context);
        THEN("returned list of TraitsDatas is as expected") { CHECK(expectedVec == actualVec); }
      }
      WHEN("batch resolve is called with kException errorPolicyTag") {
        const std::vector<openassetio::TraitsDataPtr> actualVec = manager->resolve(
            refs, traits, context, hostApi::Manager::BatchElementErrorPolicyTag::kException);
        THEN("returned list of TraitsDatas is as expected") { CHECK(expectedVec == actualVec); }
      }
      WHEN("batch resolve is called with kVariant errorPolicyTag") {
        std::vector<std::variant<openassetio::BatchElementError, openassetio::TraitsDataPtr>>
            actualVec = manager->resolve(refs, traits, context,
                                         hostApi::Manager::BatchElementErrorPolicyTag::kVariant);
        THEN("returned lists of variants contains the expected TraitsDatas") {
          CHECK(expectedVec.size() == actualVec.size());
          for (size_t i = 0; i < actualVec.size(); ++i) {
            CHECK(std::holds_alternative<openassetio::TraitsDataPtr>(actualVec[i]));
            auto actualVal = std::get<openassetio::TraitsDataPtr>(actualVec[i]);
            CHECK(expectedVec[i].get() == actualVal.get());
          }
        }
      }
    }
    GIVEN("manager plugin successfully resolves multiple entity references in a non-index order") {
      const openassetio::EntityReferences refs = {openassetio::EntityReference{"testReference1"},
                                                  openassetio::EntityReference{"testReference2"},
                                                  openassetio::EntityReference{"testReference3"}};

      const openassetio::TraitsDataPtr expected1 = openassetio::TraitsData::make();
      expected1->addTrait("aTestTrait1");
      const openassetio::TraitsDataPtr expected2 = openassetio::TraitsData::make();
      expected2->addTrait("aTestTrait2");
      const openassetio::TraitsDataPtr expected3 = openassetio::TraitsData::make();
      expected3->addTrait("aTestTrait3");
      std::vector<openassetio::TraitsDataPtr> expectedVec{expected1, expected2, expected3};

      // With success callback side effect, given out of order.
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_5(2, expectedVec[2]))
          .LR_SIDE_EFFECT(_5(0, expectedVec[0]))
          .LR_SIDE_EFFECT(_5(1, expectedVec[1]));

      WHEN("batch resolve is called with default errorPolicyTag") {
        const std::vector<openassetio::TraitsDataPtr> actualVec =
            manager->resolve(refs, traits, context);
        THEN("returned list of TraitsDatas is ordered in index order") {
          CHECK(expectedVec == actualVec);
        }
      }
      WHEN("batch resolve is called with kException errorPolicyTag") {
        const std::vector<openassetio::TraitsDataPtr> actualVec = manager->resolve(
            refs, traits, context, hostApi::Manager::BatchElementErrorPolicyTag::kException);
        THEN("returned list of TraitsDatas is ordered in index order") {
          CHECK(expectedVec == actualVec);
        }
      }
      WHEN("batch resolve is called with kVariant errorPolicyTag") {
        std::vector<std::variant<openassetio::BatchElementError, openassetio::TraitsDataPtr>>
            actualVec = manager->resolve(refs, traits, context,
                                         hostApi::Manager::BatchElementErrorPolicyTag::kVariant);
        THEN("returned lists of variants is ordered in index order") {
          CHECK(expectedVec.size() == actualVec.size());
          for (size_t i = 0; i < actualVec.size(); ++i) {
            CHECK(std::holds_alternative<openassetio::TraitsDataPtr>(actualVec[i]));
            auto actualVal = std::get<openassetio::TraitsDataPtr>(actualVec[i]);
            CHECK(expectedVec[i].get() == actualVal.get());
          }
        }
      }
    }
    GIVEN(
        "manager plugin will encounter an entity-specific error when next resolving a reference") {
      const openassetio::EntityReference ref = openassetio::EntityReference{"testReference"};
      const openassetio::EntityReferences refs = {ref};

      openassetio::BatchElementError expected{
          openassetio::BatchElementError::ErrorCode::kMalformedEntityReference, "Error Message"};

      // With error callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_6(0, expected));

      WHEN("singular resolve is called with default errorPolicyTag") {
        THEN("an exception is thrown") {
          CHECK_THROWS_MATCHES(manager->resolve(ref, traits, context),
                               openassetio::MalformedEntityReferenceBatchElementException,
                               Catch::Message("Error Message"));
        }
      }
      WHEN("singular resolve is called with kException errorPolicyTag") {
        THEN("an exception is thrown") {
          CHECK_THROWS_MATCHES(
              manager->resolve(ref, traits, context,
                               hostApi::Manager::BatchElementErrorPolicyTag::kException),
              openassetio::MalformedEntityReferenceBatchElementException,
              Catch::Message("Error Message"));
        }
      }
      WHEN("singular resolve is called with kVariant errorPolicyTag") {
        std::variant<openassetio::BatchElementError, openassetio::TraitsDataPtr> actual =
            manager->resolve(ref, traits, context,
                             hostApi::Manager::BatchElementErrorPolicyTag::kVariant);
        THEN("returned variant contains the expected BatchElementError") {
          CHECK(std::holds_alternative<openassetio::BatchElementError>(actual));
          const auto& actualVal = std::get<openassetio::BatchElementError>(actual);
          CHECK(expected == actualVal);
          // TODO(EM): BatchElementError is currently copied, but we
          //  may switch this to move semantics.
          // https://github.com/OpenAssetIO/OpenAssetIO/issues/858
          CHECK_FALSE(expected.message.data() == actualVal.message.data());
        }
      }
    }
    GIVEN(
        "manager plugin will encounter entity-specific errors when next resolving multiple "
        "references") {
      const openassetio::EntityReferences refs = {openassetio::EntityReference{"testReference1"},
                                                  openassetio::EntityReference{"testReference2"},
                                                  openassetio::EntityReference{"testReference3"}};

      const openassetio::TraitsDataPtr expectedValue2 = openassetio::TraitsData::make();
      expectedValue2->addTrait("aTestTrait");
      const openassetio::BatchElementError expectedError0{
          openassetio::BatchElementError::ErrorCode::kMalformedEntityReference,
          "Malformed Mock Error🤖"};
      const openassetio::BatchElementError expectedError1{
          openassetio::BatchElementError::ErrorCode::kEntityAccessError,
          "Entity Access Error Message"};

      // With mixed callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_5(2, expectedValue2))
          .LR_SIDE_EFFECT(_6(0, expectedError0))
          .LR_SIDE_EFFECT(_6(1, expectedError1));

      WHEN("batch resolve is called with default errorPolicyTag") {
        THEN("an exception is thrown") {
          CHECK_THROWS_MATCHES(manager->resolve(refs, traits, context),
                               openassetio::MalformedEntityReferenceBatchElementException,
                               Catch::Message("Malformed Mock Error🤖"));
        }
      }
      WHEN("batch resolve is called with kException errorPolicyTag") {
        THEN("an exception is thrown") {
          CHECK_THROWS_MATCHES(
              manager->resolve(refs, traits, context,
                               hostApi::Manager::BatchElementErrorPolicyTag::kException),
              openassetio::MalformedEntityReferenceBatchElementException,
              Catch::Message("Malformed Mock Error🤖"));
        }
      }
      WHEN("batch resolve is called with kVariant errorPolicyTag") {
        std::vector<std::variant<openassetio::BatchElementError, openassetio::TraitsDataPtr>>
            actualVec = manager->resolve(refs, traits, context,
                                         hostApi::Manager::BatchElementErrorPolicyTag::kVariant);
        THEN("returned lists of variants contains the expected objects") {
          auto error0 = std::get<openassetio::BatchElementError>(actualVec[0]);
          CHECK(error0 == expectedError0);

          auto error1 = std::get<openassetio::BatchElementError>(actualVec[1]);
          CHECK(error1 == expectedError1);

          CHECK(std::get<openassetio::TraitsDataPtr>(actualVec[2]) == expectedValue2);
        }
      }
    }
  }
}

using ErrorCode = openassetio::BatchElementError::ErrorCode;

template <class T, ErrorCode C>
struct BatchElementErrorMapping {
  using ExceptionType = T;
  static constexpr ErrorCode kErrorCode = C;
};

TEMPLATE_TEST_CASE(
    "BatchElementError conversion to exceptions when resolving", "",
    (BatchElementErrorMapping<openassetio::UnknownBatchElementException, ErrorCode::kUnknown>),
    (BatchElementErrorMapping<openassetio::InvalidEntityReferenceBatchElementException,
                              ErrorCode::kInvalidEntityReference>),
    (BatchElementErrorMapping<openassetio::MalformedEntityReferenceBatchElementException,
                              ErrorCode::kMalformedEntityReference>),
    (BatchElementErrorMapping<openassetio::EntityAccessErrorBatchElementException,
                              ErrorCode::kEntityAccessError>),
    (BatchElementErrorMapping<openassetio::EntityResolutionErrorBatchElementException,
                              ErrorCode::kEntityResolutionError>)) {
  namespace hostApi = openassetio::hostApi;
  using trompeloeil::_;

  using ExpectedExceptionType = typename TestType::ExceptionType;
  static constexpr ErrorCode kExpectedErrorCode = TestType::kErrorCode;

  GIVEN("a configured Manager instance") {
    const openassetio::trait::TraitSet traits = {"fakeTrait", "secondFakeTrait"};
    const openassetio::ManagerFixture fixture;
    const auto& manager = fixture.manager;
    auto& mockManagerInterface = fixture.mockManagerInterface;
    const auto& context = fixture.context;
    const auto& hostSession = fixture.hostSession;

    AND_GIVEN(
        "manager plugin will encounter an entity-specific error when next resolving a reference") {
      const openassetio::EntityReference ref = openassetio::EntityReference{"testReference"};
      const openassetio::EntityReferences refs = {ref};

      const openassetio::BatchElementError expectedError{kExpectedErrorCode, "Some error message"};

      // With error callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_6(123, expectedError));

      WHEN("resolve is called with kException errorPolicyTag") {
        THEN("an exception is thrown") {
          try {
            manager->resolve(ref, traits, context,
                             hostApi::Manager::BatchElementErrorPolicyTag::kException);
            FAIL_CHECK("Exception not thrown");
          } catch (const ExpectedExceptionType& exc) {
            CHECK(exc.what() == expectedError.message);
            CHECK(exc.error == expectedError);
            CHECK(exc.index == 123);
          }
        }
      }
    }

    AND_GIVEN(
        "manager plugin will encounter entity-specific errors when next resolving multiple "
        "references") {
      const openassetio::EntityReferences refs = {openassetio::EntityReference{"testReference1"},
                                                  openassetio::EntityReference{"testReference2"}};

      const openassetio::BatchElementError expectedError{kExpectedErrorCode, "Some error"};

      // With error callback side effect
      REQUIRE_CALL(mockManagerInterface, resolve(refs, traits, context, hostSession, _, _))
          .LR_SIDE_EFFECT(_6(123, expectedError))
          .LR_SIDE_EFFECT(FAIL_CHECK("Exception should have short-circuited this"));

      WHEN("resolve is called with kException errorPolicyTag") {
        THEN("an exception is thrown") {
          try {
            manager->resolve(refs, traits, context,
                             hostApi::Manager::BatchElementErrorPolicyTag::kException);
            FAIL_CHECK("Exception not thrown");
          } catch (const ExpectedExceptionType& exc) {
            CHECK(exc.what() == expectedError.message);
            CHECK(exc.error == expectedError);
            CHECK(exc.index == 123);
          }
        }
      }
    }
  }
}
