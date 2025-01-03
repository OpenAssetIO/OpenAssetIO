// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <algorithm>
#include <iterator>
#include <memory>
#include <tuple>
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/log/SeverityFilter.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerImplementationFactory.hpp>
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/pluginSystem/HybridPluginSystemManagerImplementationFactory.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>

namespace {

#define CLASS_AND_PTRS(Class) std::tuple<Class, Class##Ptr, Class##ConstPtr>

namespace hostApi = openassetio::hostApi;
namespace log = openassetio::log;
namespace managerApi = openassetio::managerApi;
namespace pluginSystem = openassetio::pluginSystem;

// clang-format off
using ClassesWithPtrAlias = std::tuple<
    CLASS_AND_PTRS(openassetio::Context),
    CLASS_AND_PTRS(openassetio::trait::TraitsData),
    CLASS_AND_PTRS(hostApi::EntityReferencePager),
    CLASS_AND_PTRS(hostApi::HostInterface),
    CLASS_AND_PTRS(hostApi::Manager),
    CLASS_AND_PTRS(hostApi::ManagerFactory),
    CLASS_AND_PTRS(hostApi::ManagerImplementationFactoryInterface),
    CLASS_AND_PTRS(log::ConsoleLogger),
    CLASS_AND_PTRS(log::LoggerInterface),
    CLASS_AND_PTRS(log::SeverityFilter),
    CLASS_AND_PTRS(managerApi::EntityReferencePagerInterface),
    CLASS_AND_PTRS(managerApi::Host),
    CLASS_AND_PTRS(managerApi::HostSession),
    CLASS_AND_PTRS(managerApi::ManagerInterface),
    CLASS_AND_PTRS(managerApi::ManagerStateBase),
    CLASS_AND_PTRS(pluginSystem::CppPluginSystem),
    CLASS_AND_PTRS(pluginSystem::CppPluginSystemManagerImplementationFactory),
    CLASS_AND_PTRS(pluginSystem::CppPluginSystemManagerPlugin),
    CLASS_AND_PTRS(pluginSystem::CppPluginSystemPlugin),
    CLASS_AND_PTRS(pluginSystem::HybridPluginSystemManagerImplementationFactory)
>;
// clang-format on
}  // namespace

// NOLINTNEXTLINE(cppcoreguidelines-avoid-non-const-global-variables,cppcoreguidelines-avoid-c-arrays)
TEMPLATE_LIST_TEST_CASE("Appropriate classes have shared_ptr aliases", "", ClassesWithPtrAlias) {
  using Class = std::tuple_element_t<0, TestType>;
  using ClassPtr = std::tuple_element_t<1, TestType>;
  using ClassConstPtr = std::tuple_element_t<2, TestType>;

  STATIC_REQUIRE(std::is_same_v<ClassPtr, std::shared_ptr<Class>>);
  STATIC_REQUIRE(std::is_same_v<ClassConstPtr, std::shared_ptr<const Class>>);
  STATIC_REQUIRE(std::is_same_v<typename Class::Ptr, ClassPtr>);
  STATIC_REQUIRE(std::is_same_v<typename Class::ConstPtr, ClassConstPtr>);
}

SCENARIO("TraitSet supports set operations") {
  using openassetio::trait::TraitsData;
  using openassetio::trait::TraitSet;

  GIVEN("two trait sets") {
    const TraitSet traitsA{"a", "b", "c"};
    const TraitSet traitsB{"d", "c", "b"};

    WHEN("union is performed") {
      TraitSet actualUnion;
      std::set_union(cbegin(traitsA), cend(traitsA), cbegin(traitsB), cend(traitsB),
                     std::inserter(actualUnion, end(actualUnion)));

      THEN("union is correct") {
        const TraitSet expectedUnion{"a", "b", "c", "d"};
        CHECK(actualUnion == expectedUnion);
      }
    }

    WHEN("intersection is performed") {
      TraitSet actualIntersection;
      std::set_intersection(cbegin(traitsA), cend(traitsA), cbegin(traitsB), cend(traitsB),
                            std::inserter(actualIntersection, end(actualIntersection)));
      THEN("intersection is correct") {
        const TraitSet expectedIntersection{"b", "c"};
        CHECK(actualIntersection == expectedIntersection);
      }
    }

    WHEN("non-subset is checked for inclusion in set A") {
      const bool isSubset =
          std::includes(cbegin(traitsA), cend(traitsA), cbegin(traitsB), cend(traitsB));

      THEN("A is not a subset of B") { CHECK(!isSubset); }
    }

    AND_GIVEN("a subset of set A") {
      const TraitSet subset{"c", "a"};

      WHEN("subset is checked for inclusion in set A") {
        const bool isSubset =
            std::includes(cbegin(traitsA), cend(traitsA), cbegin(subset), cend(subset));

        THEN("subset is detected as included in A") { CHECK(isSubset); }
      }
    }

    GIVEN("an TraitsData initialized with a TraitSet") {
      const TraitSet traits{"a", "b", "c"};
      const auto traitsData = TraitsData::make(traits);

      WHEN("the trait set is retrieved") {
        const auto actualTraits = traitsData->traitSet();

        THEN("it is of type TraitSet") {
          CHECK(std::is_same_v<const TraitSet, decltype(actualTraits)>);
        }
      }
    }
  }
}
