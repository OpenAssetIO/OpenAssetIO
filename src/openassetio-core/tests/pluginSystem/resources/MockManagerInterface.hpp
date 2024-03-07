// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <trompeloeil.hpp>

#include <openassetio/managerApi/ManagerInterface.hpp>

struct MockManagerInterface
    : trompeloeil::mock_interface<openassetio::managerApi::ManagerInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK0(info);
  IMPLEMENT_MOCK2(initialize);
  IMPLEMENT_MOCK1(hasCapability);
  IMPLEMENT_MOCK4(managementPolicy);
  IMPLEMENT_MOCK2(isEntityReferenceString);
  IMPLEMENT_MOCK5(entityExists);
  IMPLEMENT_MOCK7(resolve);
  IMPLEMENT_MOCK7(preflight);
  IMPLEMENT_MOCK7(register_);
};
