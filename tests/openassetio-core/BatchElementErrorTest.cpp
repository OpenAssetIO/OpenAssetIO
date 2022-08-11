// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <string>
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/BatchElementError.hpp>

using openassetio::BatchElementError;

SCENARIO("BatchElementError usage") {
  GIVEN("an error code and message") {
    const auto code = BatchElementError::ErrorCode::kUnknown;
    const std::string message = "some message";

    WHEN("a BatchElementError is constructed wrapping the code and message") {
      BatchElementError error{code, message};

      THEN("code and message cannot be modified") {
        STATIC_REQUIRE(std::is_const_v<decltype(error.code)>);
        STATIC_REQUIRE(std::is_const_v<decltype(error.message)>);
      }

      THEN("code and message are available for querying") {
        CHECK(error.code == BatchElementError::ErrorCode::kUnknown);
        CHECK(error.message == "some message");
      }
    }
  }
}
