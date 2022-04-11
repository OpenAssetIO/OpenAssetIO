// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <string_view>
#include <type_traits>

#include <openassetio/c/StringView.h>

#include <catch2/catch.hpp>

#include <openassetio/typedefs.hpp>

#include "StringViewReporting.hpp"

SCENARIO("Creating, modifying and querying a C API mutable StringView") {
  GIVEN("A populated C++ string") {
    openassetio::Str expectedStr = "some string";

    WHEN("a StringView is constructed wrapping the buffer") {
      OPENASSETIO_NS(StringView)
      actualStringView{expectedStr.size(), expectedStr.data(), expectedStr.size()};

      THEN("StringView can be interrogated to reveal the values at construction") {
        CHECK(actualStringView.capacity == expectedStr.size());
        CHECK(actualStringView.size == expectedStr.size());
        CHECK(actualStringView == expectedStr);
      }

      AND_WHEN("string is modified through the StringView") {
        STATIC_REQUIRE(std::is_const_v<decltype(actualStringView.capacity)>);
        actualStringView.data[1] = '0';
        actualStringView.size = 4;

        THEN("storage has been updated") { CHECK(expectedStr == "s0me string"); }

        THEN("view has been updated") { CHECK(actualStringView == "s0me"); }
      }
    }
  }
}

SCENARIO("Creating and querying a C API immutable ConstStringView") {
  GIVEN("A char buffer storing a string") {
    openassetio::Str expectedStr;
    expectedStr = "some string";

    WHEN("a ConstStringView is constructed wrapping the buffer") {
      OPENASSETIO_NS(ConstStringView) actualStringView{expectedStr.data(), expectedStr.size()};

      THEN("ConstStringView can be interrogated to reveal the values at construction") {
        CHECK(actualStringView.size == expectedStr.size());
        CHECK(actualStringView.data == expectedStr.data());
        CHECK(actualStringView == expectedStr);
      }

      THEN("string cannot be modified through the ConstStringView") {
        STATIC_REQUIRE(std::is_const_v<decltype(actualStringView.data)>);
        STATIC_REQUIRE(
            std::is_const_v<std::remove_reference_t<decltype(actualStringView.data[0])>>);
        STATIC_REQUIRE(std::is_const_v<decltype(actualStringView.size)>);
      }
    }
  }
}
