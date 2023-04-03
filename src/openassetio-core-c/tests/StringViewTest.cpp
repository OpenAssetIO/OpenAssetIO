// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <string_view>
#include <type_traits>

#include <openassetio/c/StringView.h>

#include <catch2/catch.hpp>

#include <openassetio/typedefs.hpp>

// Private headers
#include <StringView.hpp>

#include "StringViewReporting.hpp"

SCENARIO("Creating, modifying and querying a C API mutable StringView") {
  GIVEN("A populated C++ string") {
    openassetio::Str expectedStr = "some string";

    WHEN("a StringView is constructed wrapping the C++ string") {
      oa_StringView actualStringView{expectedStr.size(), expectedStr.data(), expectedStr.size()};

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

    AND_GIVEN("a StringView wrapping a buffer with sufficient capacity for C++ string") {
      openassetio::Str storage(expectedStr.size(), '\0');

      oa_StringView actualStringView{storage.size(), storage.data(), 0};

      WHEN("assignStringView is used to copy the C++ string to the StringView") {
        openassetio::assignStringView(&actualStringView, expectedStr);

        THEN("Source string was copied to StringView") {
          CHECK(actualStringView == expectedStr);
          CHECK(actualStringView.data != expectedStr.data());
        }
      }
    }

    AND_GIVEN("a StringView wrapping a buffer with insufficient capacity for C++ string") {
      openassetio::Str storage(3, '\0');

      oa_StringView actualStringView{storage.size(), storage.data(), 0};

      WHEN("assignStringView is used to copy the C++ string to the StringView") {
        openassetio::assignStringView(&actualStringView, expectedStr);

        THEN("StringView matches truncated string") { CHECK(actualStringView == "som"); }
      }
    }
  }

  GIVEN("A C string literal") {
    constexpr const char* kExpectedStr = "some string";

    AND_GIVEN("a StringView wrapping a buffer with sufficient capacity") {
      openassetio::Str storage(std::string_view(kExpectedStr).size(), '\0');

      oa_StringView actualStringView{storage.size(), storage.data(), 0};

      WHEN("assignStringView is used to copy the string literal to the StringView") {
        openassetio::assignStringView(&actualStringView, kExpectedStr);

        THEN("StringView matches source string") { CHECK(actualStringView == kExpectedStr); }
      }
    }
  }
}

SCENARIO("Creating and querying a C API immutable ConstStringView") {
  GIVEN("A char buffer storing a string") {
    openassetio::Str expectedStr;
    expectedStr = "some string";

    WHEN("a ConstStringView is constructed wrapping the buffer") {
      const oa_ConstStringView actualStringView{expectedStr.data(), expectedStr.size()};

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
