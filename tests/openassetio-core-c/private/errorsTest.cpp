// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <catch2/catch.hpp>

#include <openassetio/c/SimpleString.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>
// private headers
#include <errors.hpp>

SCENARIO("throwIfError error code/message handling") {
  GIVEN("an OK error code") {
    const int code = OPENASSETIO_NS(kOK);

    WHEN("throwIfError is called") {
      THEN("no exception is thrown") {
        openassetio::throwIfError(code, OPENASSETIO_NS(SimpleString){});
      }
    }
  }

  GIVEN("an error code and message") {
    const int code = 123;
    openassetio::Str message = "some error";

    OPENASSETIO_NS(SimpleString)
    cmessage{
        message.size(),
        message.data(),
        message.size(),
    };

    WHEN("throwIfError is called") {
      THEN("expected exception is thrown") {
        REQUIRE_THROWS_MATCHES(openassetio::throwIfError(code, cmessage), std::runtime_error,
                               Catch::Message("123: some error"));
      }
    }
  }
}
