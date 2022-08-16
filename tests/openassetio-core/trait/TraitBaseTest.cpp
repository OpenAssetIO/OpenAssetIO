// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/trait/TraitBase.hpp>
#include <openassetio/typedefs.hpp>

#include <catch2/catch.hpp>
#include "openassetio/TraitsData.hpp"

namespace {

using openassetio::TraitsData;
using openassetio::TraitsDataPtr;
using std::string;
namespace trait = openassetio::trait;

// TraitBase can't be tested directly, so we derive a test trait.
struct TestTrait : trait::TraitBase<TestTrait> {
 private:
  static inline const trait::property::Key kSomeProperty{"some property"};

 public:
  static inline const trait::TraitId kId{"test"};

  using TraitBase<TestTrait>::TraitBase;

  [[nodiscard]] trait::TraitPropertyStatus getSomeProperty(std::string* out) const {
    return getTraitProperty(out, kId, kSomeProperty);
  }

  void setSomeProperty(const std::string& value) {
    data()->setTraitProperty(kId, kSomeProperty, value);
  }

  // Helpers for tests

  [[nodiscard]] TraitsDataPtr& dataPtr() { return data(); }
  [[nodiscard]] const TraitsDataPtr& dataPtr() const { return data(); }
};

SCENARIO("Retrieving the undelying data") {
  GIVEN("Some known traits data") {
    TraitsDataPtr data = TraitsData::make();

    WHEN("a trait instance is constructed with data") {
      TestTrait trait(data);

      THEN("the supplied data is exposed via protected method") { CHECK(trait.dataPtr() == data); }

      WHEN("a const trait instance is constructed with the data") {
        const TestTrait constTrait(data);

        THEN("the supplied data is exposed via const protected method") {
          CHECK(constTrait.dataPtr() == data);
        }
      }
    }
  }
}

SCENARIO("Checking a trait is valid") {
  GIVEN("Some known traits data") {
    TraitsDataPtr data = TraitsData::make();

    AND_GIVEN("the data has the trait set") {
      data->addTrait(TestTrait::kId);

      WHEN("called") {
        TestTrait trait(data);
        THEN("isValid returns true") { CHECK(trait.isValid()); }
      }
    }

    AND_GIVEN("the data does not have trait") {
      TestTrait trait(data);
      THEN("isValid returns false") { CHECK(!trait.isValid()); }
    }
  }
}

SCENARIO("Imbuing a trait to the traits data held by a trait instance") {
  GIVEN("Some known traits data held by a trait") {
    TraitsDataPtr data = TraitsData::make();
    TestTrait trait(data);

    AND_GIVEN("the data does not have the trait set") {
      WHEN("the trait is imbued") {
        trait.imbue();
        THEN("trait is added") { CHECK(data->hasTrait(TestTrait::kId)); }
      }
    }

    AND_GIVEN("the data does have the trait set") {
      data->addTrait(TestTrait::kId);

      WHEN("the trait is imbued") {
        THEN("is a noop") {
          TraitsDataPtr oldData = TraitsData::make(data);
          trait.imbue();
          CHECK(*data == *oldData);
        }
      }
    }
  }
}

SCENARIO("Imbuing a trait to an arbitrary traits data instance") {
  GIVEN("Some known traits data") {
    TraitsDataPtr data = TraitsData::make();

    AND_GIVEN("the data does not have the trait set") {
      WHEN("the trait is imbued to the data") {
        TestTrait::imbueTo(data);
        THEN("the trait is added to the supplied data") { CHECK(data->hasTrait(TestTrait::kId)); }
      }
    }
    AND_GIVEN("the data does have the trait set") {
      data->addTrait(TestTrait::kId);
      WHEN("the trait is imbued to the data") {
        THEN("is a noop") {
          TraitsDataPtr oldData = TraitsData::make(data);
          TestTrait::imbueTo(data);
          CHECK(*data == *oldData);
        }
      }
    }
  }
}

}  // namespace
