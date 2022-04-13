// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>

// private headers
#include <errors.hpp>

#include "StringViewReporting.hpp"

SCENARIO("throwIfError error code/message handling") {
  using openassetio::errors::throwIfError;

  GIVEN("an OK error code") {
    const int code = OPENASSETIO_NS(kOK);

    WHEN("throwIfError is called") {
      THEN("no exception is thrown") { throwIfError(code, OPENASSETIO_NS(StringView){}); }
    }
  }

  GIVEN("an error code and message") {
    const int code = 123;
    openassetio::Str message = "some error";

    OPENASSETIO_NS(StringView)
    cmessage{
        message.size(),
        message.data(),
        message.size(),
    };

    WHEN("throwIfError is called") {
      THEN("expected exception is thrown") {
        REQUIRE_THROWS_MATCHES(throwIfError(code, cmessage), std::runtime_error,
                               Catch::Message("123: some error"));
      }
    }
  }
}

SCENARIO("Using extractExceptionMessage to copy a C++ exception message to a C StringView") {
  using openassetio::errors::extractExceptionMessage;

  GIVEN("An exception and a StringView") {
    const openassetio::Str expectedMessage = "some error";
    const std::runtime_error runtimeError{expectedMessage};

    openassetio::Str storage(expectedMessage.size(), '\0');
    OPENASSETIO_NS(StringView) actualMessage{storage.capacity(), storage.data(), 0};

    WHEN("extractExceptionMessage copies the message from the exception to the StringView") {
      extractExceptionMessage(&actualMessage, runtimeError);

      // Sanity check that `what()` always returns the same pointer on
      // this platform.
      CHECK(static_cast<const void*>(runtimeError.what()) ==
            static_cast<const void*>(runtimeError.what()));

      THEN("Message is copied into StringView") {
        CHECK(actualMessage == expectedMessage);
        CHECK(actualMessage.data != runtimeError.what());
      }
    }
  }
}
