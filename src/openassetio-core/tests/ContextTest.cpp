// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/Context.hpp>

OPENASSETIO_FWD_DECLARE(TraitsData)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerStateBase)

using openassetio::Context;

SCENARIO("Context constructor is private") {
  STATIC_REQUIRE_FALSE(
      std::is_constructible_v<Context, Context::Access, openassetio::TraitsDataPtr,
                              openassetio::managerApi::ManagerStateBasePtr>);
}
