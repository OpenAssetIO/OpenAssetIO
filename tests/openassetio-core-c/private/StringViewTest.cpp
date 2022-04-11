// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <string_view>
#include <type_traits>

#include <openassetio/c/StringView.h>

#include <catch2/catch.hpp>

#include <openassetio/typedefs.hpp>

SCENARIO("Creating, modifying and querying a C API mutable StringView") {
  GIVEN("A populated C++ string") {
    openassetio::Str expectedStr = "some string";

    WHEN("a StringView is constructed wrapping the buffer") {
      OPENASSETIO_NS(StringView)
      actualStringView{expectedStr.size(), expectedStr.data(), expectedStr.size()};

      THEN("StringView can be interrogated to reveal the values at construction") {
        CHECK(actualStringView.capacity == expectedStr.size());
        CHECK(actualStringView.size == expectedStr.size());
        CHECK(std::string_view{actualStringView.data, actualStringView.size} == expectedStr);
      }

      AND_WHEN("string is modified through the StringView") {
        STATIC_REQUIRE(std::is_const_v<decltype(actualStringView.capacity)>);
        actualStringView.data[1] = '0';
        actualStringView.size = 4;

        THEN("storage has been updated") { CHECK(expectedStr == "s0me string"); }

        THEN("view has been updated") {
          CHECK(std::string_view{actualStringView.data, actualStringView.size} == "s0me");
        }
      }
    }
  }
}
