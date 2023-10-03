// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <memory>
#include <tuple>

#include <catch2/catch.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/log/SeverityFilter.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitsData.hpp>

namespace {

#define CLASS_AND_PTRS(Class) std::tuple<Class, Class##Ptr, Class##ConstPtr>

namespace hostApi = openassetio::hostApi;
namespace log = openassetio::log;
namespace managerApi = openassetio::managerApi;

// clang-format off
using ClassesWithPtrAlias = std::tuple<
    CLASS_AND_PTRS(openassetio::Context),
    CLASS_AND_PTRS(openassetio::trait::TraitsData),
    CLASS_AND_PTRS(hostApi::HostInterface),
    CLASS_AND_PTRS(hostApi::Manager),
    CLASS_AND_PTRS(hostApi::ManagerFactory),
    CLASS_AND_PTRS(hostApi::ManagerImplementationFactoryInterface),
    CLASS_AND_PTRS(log::ConsoleLogger),
    CLASS_AND_PTRS(log::LoggerInterface),
    CLASS_AND_PTRS(log::SeverityFilter),
    CLASS_AND_PTRS(managerApi::Host),
    CLASS_AND_PTRS(managerApi::HostSession),
    CLASS_AND_PTRS(managerApi::ManagerInterface),
    CLASS_AND_PTRS(managerApi::ManagerStateBase)
>;
// clang-format on
}  // namespace

TEMPLATE_LIST_TEST_CASE("Appropriate classes have shared_ptr aliases", "", ClassesWithPtrAlias) {
  using Class = std::tuple_element_t<0, TestType>;
  using ClassPtr = std::tuple_element_t<1, TestType>;
  using ClassConstPtr = std::tuple_element_t<2, TestType>;

  STATIC_REQUIRE(std::is_same_v<ClassPtr, std::shared_ptr<Class>>);
  STATIC_REQUIRE(std::is_same_v<ClassConstPtr, std::shared_ptr<const Class>>);
  STATIC_REQUIRE(std::is_same_v<typename Class::Ptr, ClassPtr>);
  STATIC_REQUIRE(std::is_same_v<typename Class::ConstPtr, ClassConstPtr>);
}
