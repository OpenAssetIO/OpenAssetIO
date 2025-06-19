// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/macros.hpp>
#include <openassetio/managerApi/Host.hpp>

OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)

SCENARIO("Host constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<openassetio::managerApi::Host,
                                               openassetio::hostApi::HostInterfacePtr>);
}
