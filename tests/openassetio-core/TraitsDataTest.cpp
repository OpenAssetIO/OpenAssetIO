// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>

using openassetio::Int;
using openassetio::TraitsData;
using openassetio::TraitsDataPtr;
using openassetio::trait::property::Key;
using openassetio::trait::property::Value;

SCENARIO("TraitsData constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<TraitsData>);
}

SCENARIO("TraitsData trait set constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<TraitsData, const openassetio::trait::TraitSet&>);
}

SCENARIO("TraitsData copy constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<TraitsData, const openassetio::TraitsData&>);
}

SCENARIO("TraitsData make from other creates a deep copy") {
  GIVEN("an instance with existing data") {
    TraitsDataPtr data = TraitsData::make();
    data->setTraitProperty("a", "a", Int(1));
    WHEN("a copy is made using the make copy constructor") {
      TraitsDataPtr copy = TraitsData::make(data);
      WHEN("existing values are queried") {
        THEN("property data has been copied") {
          Value someValue;
          Int value;
          REQUIRE(copy->getTraitProperty(&someValue, "a", "a"));
          value = *std::get_if<Int>(&someValue);
          CHECK(value == Int(1));
        }
      }
      AND_WHEN("the data is modified") {
        data->setTraitProperty("a", "a", Int(3));
        THEN("the copy is unchanged") {
          Value someValue;
          Int value;
          REQUIRE(copy->getTraitProperty(&someValue, "a", "a"));
          value = *std::get_if<Int>(&someValue);
          CHECK(value == Int(1));
        }
      }
    }
  }
}
