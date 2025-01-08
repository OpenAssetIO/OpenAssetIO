// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <algorithm>
#include <memory>
#include <sstream>
#include <string>

#include <fmt/format.h>
#include <catch2/catch.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/utils/ostream.hpp>

#include <utils/formatter.hpp>

namespace {

template <typename T>
void checkBasicPrintable(const T& value, const std::string& expected) {
  // Check fmt::format
  REQUIRE(fmt::format("{}", value) == expected);

  // Check stream operator
  std::ostringstream oss;
  oss << value;
  REQUIRE(oss.str() == expected);
}

template <typename T>
void checkBasicPrintableContains(const T& value, const std::string& expected) {
  // Check fmt::format
  REQUIRE_THAT(fmt::format("{}", value), Catch::Matchers::Contains(expected));

  // Check stream operator
  std::ostringstream oss;
  oss << value;
  REQUIRE_THAT(oss.str(), Catch::Matchers::Contains(expected));
}

// This function is here because we can't assume order of set and map types.
// Doing this characterwise check is _almost_ just as good.
template <typename T>
void checkBasicPrintableByCharacters(const T& value, const std::string& expected) {
  auto sortedExpected = expected;
  std::sort(sortedExpected.begin(), sortedExpected.end());

  // Check fmt::format
  auto sortedValueFromFmt = fmt::format("{}", value);
  std::sort(sortedValueFromFmt.begin(), sortedValueFromFmt.end());
  REQUIRE(sortedValueFromFmt == sortedExpected);

  // Check stream operator
  std::ostringstream oss;
  oss << value;
  auto sortedValueFromOstream = oss.str();
  std::sort(sortedValueFromOstream.begin(), sortedValueFromOstream.end());
  REQUIRE(sortedValueFromOstream == sortedExpected);
}

}  // namespace

SCENARIO("Printing api types") {
  GIVEN("Printable OpenAssetIO Types") {
    openassetio::errors::BatchElementError batchElementError;
    batchElementError.code = openassetio::errors::BatchElementError::ErrorCode::kInvalidTraitSet;
    batchElementError.message = "Invalid trait set";

    const openassetio::EntityReference entityReference("test:///an_entity_reference");

    openassetio::EntityReferences entityReferences;
    entityReferences.emplace_back("test:///an_entity_reference_1");
    entityReferences.emplace_back("test:///an_entity_reference_2");

    const openassetio::trait::TraitSet traitSet = {"trait1", "trait2"};
    const openassetio::trait::TraitSets traitSets = {{"trait1", "trait2"}, {"trait3", "trait4"}};

    const openassetio::Identifier identifier = "an identifier";

    const openassetio::Str str = "example string";

    const openassetio::StrMap strMap = {{"key1", "value1"}, {"key2", "value2"}};

    const openassetio::InfoDictionary infoDictionary = {{"key1", openassetio::Str("value1")},
                                                        {"key2", false}};

    auto managerInterfaceCapability =
        openassetio::managerApi::ManagerInterface::Capability::kPublishing;

    auto managerCapability = openassetio::hostApi::Manager::Capability::kPublishing;

    auto context = openassetio::Context::make();

    context->locale->setTraitProperty("aTrait", "aIntTraitProperty", 2);
    context->managerState = std::make_shared<openassetio::managerApi::ManagerStateBase>();

    openassetio::trait::TraitsDataPtr traitsData = openassetio::trait::TraitsData::make();
    traitsData->setTraitProperty("aTrait", "aIntTraitProperty", 2);
    traitsData->setTraitProperty("aTrait", "aBoolTraitProperty", false);
    traitsData->setTraitProperty("a.long.namespaced.trait.that.goes.on.and.on.and.on",
                                 "aIntTraitProperty", 2);
    traitsData->setTraitProperty("a.long.namespaced.trait.that.goes.on.and.on.and.on",
                                 "aStringTraitProperty", openassetio::Str("a string"));
    traitsData->setTraitProperty("a.long.namespaced.trait.that.goes.on.and.on.and.on",
                                 "aBoolTraitProperty", true);
    traitsData->addTrait("a.trait.with.no.properties");

    WHEN("An InfoDictionary is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintableByCharacters(infoDictionary, "{'key2': False, 'key1': 'value1'}");
      }
    }

    WHEN("A TraitSet is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintableByCharacters(traitSet, "{'trait2', 'trait1'}");
      }
    }

    WHEN("TraitSets are printed") {
      THEN("They can be printed via fmt and <<") {
        checkBasicPrintableByCharacters(traitSets, "[{'trait2', 'trait1'}, {'trait4', 'trait3'}]");
      }
    }

    WHEN("A BatchElementError is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintable(batchElementError, "invalidTraitSet: Invalid trait set");
      }
    }

    WHEN("An EntityReference is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintable(entityReference, "test:///an_entity_reference");
      }
    }

    WHEN("EntityReferences are printed") {
      THEN("They can be printed via fmt and <<") {
        const openassetio::EntityReferences emptyEntityReferences;
        checkBasicPrintable(entityReferences,
                            "['test:///an_entity_reference_1', 'test:///an_entity_reference_2']");
        checkBasicPrintable(emptyEntityReferences, "[]");
      }
    }

    WHEN("An Identifier is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintable(identifier, "an identifier");
      }
    }

    WHEN("A Str is printed") {
      THEN("It can be printed via fmt and <<") { checkBasicPrintable(str, "example string"); }
    }

    WHEN("A StrMap is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintableByCharacters(strMap, "{'key2': 'value2', 'key1': 'value1'}");
      }
    }

    WHEN("A ManagerInterface Capability is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintable(managerInterfaceCapability, "publishing");
      }
    }

    WHEN("A Manager Capability is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintable(managerCapability, "publishing");
      }
    }

    WHEN("A Context is printed") {
      THEN("It can be printed via fmt and <<") {
        // No closing brace on purpose, to account for variant managerState memory address
        checkBasicPrintableContains(*context,
                                    R"({'locale': {'aTrait': {'aIntTraitProperty': 2}}, )"
                                    R"('managerState': 0x)");
        checkBasicPrintableContains(context, R"('locale': {'aTrait': {'aIntTraitProperty': 2}}, )"
                                             R"('managerState': 0x)");

        context = nullptr;
        checkBasicPrintable(context, "null");
      }
    }

    WHEN("A TraitsData is printed") {
      THEN("It can be printed via fmt and <<") {
        checkBasicPrintableByCharacters(
            *traitsData,
            R"({'aTrait': {'aIntTraitProperty': 2, 'aBoolTraitProperty': False}, )"
            R"('a.long.namespaced.trait.that.goes.on.and.on.and.on': {'aIntTraitProperty': 2, )"
            R"('aStringTraitProperty': 'a string', 'aBoolTraitProperty': True}, 'a.trait.with.no.properties': {}})");
        checkBasicPrintableByCharacters(
            traitsData,
            R"({'aTrait': {'aIntTraitProperty': 2, 'aBoolTraitProperty': False}, )"
            R"('a.long.namespaced.trait.that.goes.on.and.on.and.on': {'aIntTraitProperty': 2, )"
            R"('aStringTraitProperty': 'a string', 'aBoolTraitProperty': True}, 'a.trait.with.no.properties': {}})");

        traitsData = nullptr;
        checkBasicPrintable(traitsData, "null");
      }
    }
  }
}
