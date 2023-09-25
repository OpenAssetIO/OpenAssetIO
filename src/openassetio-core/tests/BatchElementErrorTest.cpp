// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <string>
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/errors/BatchElementError.hpp>

using openassetio::errors::BatchElementError;

SCENARIO("BatchElementError usage") {
  GIVEN("BatchElementError is copyable") {
    STATIC_REQUIRE(std::is_copy_assignable_v<BatchElementError>);
  }

  GIVEN("an error code and message") {
    const auto code = BatchElementError::ErrorCode::kUnknown;
    const openassetio::Str message = "some message";

    WHEN("a BatchElementError is constructed wrapping the code and message") {
      const BatchElementError error{code, message};

      THEN("code and message are available for querying") {
        CHECK(error.code == BatchElementError::ErrorCode::kUnknown);
        CHECK(error.message == "some message");
      }
    }

    WHEN("Two BatchElementErrors are constructed wrapping the same code and message") {
      const BatchElementError error{code, message};
      const BatchElementError error2{code, message};

      THEN("The errors instances match") { CHECK(error == error2); }
    }

    WHEN("Two BatchElementErrors are constructed wrapping different code and the same message") {
      const BatchElementError error{code, message};
      const BatchElementError error2{BatchElementError::ErrorCode::kEntityResolutionError,
                                     message};

      THEN("The errors instances do not match") { CHECK(error != error2); }
    }

    WHEN("Two BatchElementErrors are constructed wrapping the same code and different message") {
      const BatchElementError error{code, message};
      const BatchElementError error2{code, "another message"};

      THEN("The errors instances do not match") { CHECK(error != error2); }
    }
  }
}
