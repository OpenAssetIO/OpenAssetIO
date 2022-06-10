// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <catch2/catch.hpp>

#include <openassetio/managerAPI/ManagerStateBase.hpp>

using openassetio::managerAPI::ManagerStateBase;

namespace {

struct TestState : ManagerStateBase {
  ~TestState() override = default;
};

}  // namespace

SCENARIO("Instantiating a custom state class") { [[maybe_unused]] auto _ = TestState{}; }
