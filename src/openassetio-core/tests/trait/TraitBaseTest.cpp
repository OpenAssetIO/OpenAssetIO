// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/trait/TraitBase.hpp>
#include <openassetio/typedefs.hpp>

#include <catch2/catch.hpp>
#include "openassetio/TraitsData.hpp"

namespace {

using openassetio::Str;
using openassetio::TraitsData;
using openassetio::TraitsDataPtr;
namespace trait = openassetio::trait;

// TraitBase can't be tested directly, so we derive a test trait.
struct TestTrait : trait::TraitBase<TestTrait> {
 private:
  static inline const trait::property::Key kSomeProperty{"some property"};

 public:
  static inline const trait::TraitId kId{"test"};

  using TraitBase<TestTrait>::TraitBase;

  [[nodiscard]] trait::TraitPropertyStatus getSomeProperty(Str* out) const {
    return getTraitProperty(out, kId, kSomeProperty);
  }

  void setSomeProperty(const Str& value) { data()->setTraitProperty(kId, kSomeProperty, value); }

  // Helpers for tests

  [[nodiscard]] TraitsDataPtr& dataPtr() { return data(); }
  [[nodiscard]] const TraitsDataPtr& dataPtr() const { return data(); }
};

SCENARIO("Retrieving the undelying data") {
  GIVEN("Some known traits data") {
    const TraitsDataPtr data = TraitsData::make();

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

SCENARIO("Checking a trait is imbued") {
  GIVEN("an empty TraitsData") {
    const TraitsDataPtr data = TraitsData::make();

    AND_GIVEN("an instance of a trait view wrapping the TraitsData") {
      const TestTrait trait(data);

      WHEN("the view instance is queried for the imbued status") {
        const bool isImbued = trait.isImbued();

        THEN("the view reports that the trait is not imbued") { CHECK(!isImbued); }
      }

      AND_GIVEN("the TraitsData is imbued with the view's trait") {
        data->addTrait(TestTrait::kId);

        WHEN("the view instance is queried for the imbued status") {
          const bool isImbued = trait.isImbued();

          THEN("the view reports that the trait is imbued") { CHECK(isImbued); }
        }
      }
    }

    WHEN("the TraitsData is queried for imbued status using static trait view function") {
      const bool isImbued = TestTrait::isImbuedTo(data);

      THEN("the view reports that the trait is not imbued") { CHECK(!isImbued); }
    }

    AND_GIVEN("the TraitsData is imbued with the view's trait") {
      data->addTrait(TestTrait::kId);

      WHEN("the TraitsData is queried for imbued status using static trait view function") {
        const bool isImbued = TestTrait::isImbuedTo(data);

        THEN("the view reports that the trait is imbued") { CHECK(isImbued); }
      }
    }
  }
}

SCENARIO("Imbuing a trait to the traits data held by a trait instance") {
  GIVEN("Some known traits data held by a trait") {
    const TraitsDataPtr data = TraitsData::make();
    const TestTrait trait(data);

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
          const TraitsDataPtr oldData = TraitsData::make(data);
          trait.imbue();
          CHECK(*data == *oldData);
        }
      }
    }
  }
}

SCENARIO("Imbuing a trait to an arbitrary traits data instance") {
  GIVEN("Some known traits data") {
    const TraitsDataPtr data = TraitsData::make();

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
          const TraitsDataPtr oldData = TraitsData::make(data);
          TestTrait::imbueTo(data);
          CHECK(*data == *oldData);
        }
      }
    }
  }
}

}  // namespace
