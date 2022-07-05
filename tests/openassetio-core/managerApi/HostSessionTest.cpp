// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/managerApi/HostSession.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, Host)

SCENARIO("HostSession constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<openassetio::managerApi::HostSession,
                                               openassetio::managerApi::HostPtr>);
}
