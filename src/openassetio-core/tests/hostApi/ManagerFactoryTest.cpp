// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd

#include <catch2/catch.hpp>

#include <openassetio/hostApi/ManagerFactory.hpp>

SCENARIO("ManagerDetail equality") {
  using openassetio::hostApi::ManagerFactory;

  GIVEN("two equal ManagerDetails") {
    const ManagerFactory::ManagerDetail lhs{"test-id", "Test Name", {{"key", "value"}}};
    const ManagerFactory::ManagerDetail rhs{"test-id", "Test Name", {{"key", "value"}}};

    THEN("they compare equal") {
      CHECK(lhs == rhs);
      CHECK_FALSE(lhs != rhs);
    }
  }

  GIVEN("two ManagerDetail instances with different identifiers") {
    const ManagerFactory::ManagerDetail lhs{"test-id-1", "Test Name", {{"key", "value"}}};
    const ManagerFactory::ManagerDetail rhs{"test-id-2", "Test Name", {{"key", "value"}}};

    THEN("they compare not equal") {
      CHECK_FALSE(lhs == rhs);
      CHECK(lhs != rhs);
    }
  }

  GIVEN("two ManagerDetail instances with different display names") {
    const ManagerFactory::ManagerDetail lhs{"test-id", "Test Name 1", {{"key", "value"}}};
    const ManagerFactory::ManagerDetail rhs{"test-id", "Test Name 2", {{"key", "value"}}};

    THEN("they compare not equal") {
      CHECK_FALSE(lhs == rhs);
      CHECK(lhs != rhs);
    }
  }

  GIVEN("two ManagerDetail instances with different info") {
    const ManagerFactory::ManagerDetail lhs{"test-id", "Test Name", {{"key", "value1"}}};
    const ManagerFactory::ManagerDetail rhs{"test-id", "Test Name", {{"key", "value2"}}};

    THEN("they compare not equal") {
      CHECK_FALSE(lhs == rhs);
      CHECK(lhs != rhs);
    }
  }
}
