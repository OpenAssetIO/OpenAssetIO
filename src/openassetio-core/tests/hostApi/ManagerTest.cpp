// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/hostApi/Manager.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)

SCENARIO("Manager constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<openassetio::hostApi::Manager,
                                               openassetio::managerApi::ManagerInterfacePtr>);
}
