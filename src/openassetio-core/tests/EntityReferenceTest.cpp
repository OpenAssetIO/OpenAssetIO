// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <map>
#include <set>
#include <unordered_set>

#include <catch2/catch.hpp>

#include <openassetio/EntityReference.hpp>

SCENARIO("EntityReference used in an ordered container") {
  using openassetio::EntityReference;
  GIVEN("an ordered container") {
    std::set<EntityReference> container;
    WHEN("an entity reference is added") {
      container.emplace("foo");
      container.emplace("foo");
      container.emplace("bar");
      THEN("it is found in the container") {
        CHECK(container.size() == 2);
        CHECK(container.count(EntityReference{"foo"}) == 1);
        CHECK(container.count(EntityReference{"bar"}) == 1);
      }
    }
  }
}

SCENARIO("EntityReference used in an unordered container") {
  using openassetio::EntityReference;
  GIVEN("an unordered container") {
    std::unordered_set<EntityReference> container;
    WHEN("an entity reference is added") {
      container.emplace("foo");
      container.emplace("foo");
      container.emplace("bar");
      THEN("it is found in the container") {
        CHECK(container.size() == 2);
        CHECK(container.count(EntityReference{"foo"}) == 1);
        CHECK(container.count(EntityReference{"bar"}) == 1);
      }
    }
  }
}

SCENARIO("EntityReference equality and ordering") {
  using openassetio::EntityReference;
  GIVEN("two equal entity references") {
    const EntityReference ref1{"foo"};
    const EntityReference ref2{"foo"};

    WHEN("they are compared for equality") {
      THEN("they are equal") { CHECK(ref1 == ref2); }
    }
    WHEN("they are compared for non-equality") {
      THEN("they are equal") { CHECK_FALSE(ref1 != ref2); }
    }
    WHEN("they are compared less than or equal") {
      THEN("they are equal") {
        CHECK(ref1 <= ref2);
        CHECK(ref2 <= ref1);
      }
    }
    WHEN("they are compared greater than or equal") {
      THEN("they are equal") {
        CHECK(ref1 >= ref2);
        CHECK(ref2 >= ref1);
      }
    }
  }
  GIVEN("two unequal entity references") {
    const EntityReference ref1{"bar"};
    const EntityReference ref2{"foo"};

    WHEN("they are compared for non-equality") {
      THEN("they are not equal") { CHECK_FALSE(ref1 == ref2); }
    }
    WHEN("they are compared for non-equality") {
      THEN("they are not equal") { CHECK(ref1 != ref2); }
    }
    WHEN("they are compared for greater than") {
      THEN("they are ordered lexicographically") { CHECK(ref1 < ref2); }
    }
    WHEN("they are compared for greater than") {
      THEN("they are ordered lexicographically") { CHECK(ref2 > ref1); }
    }
    WHEN("they are compared less than or equal") {
      THEN("they are ordered lexicographically") { CHECK(ref1 <= ref2); }
    }
    WHEN("they are compared greater than or equal") {
      THEN("they are ordered lexicographically") { CHECK(ref2 >= ref1); }
    }
  }
}
