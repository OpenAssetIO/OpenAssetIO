// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

#include <openassetio/TraitsData.hpp>
#include <openassetio/trait/TraitsData.hpp>

// Disable deprecation warning that triggers -Werror, failing the build.
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#elif defined(__GNUC__)
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#endif

// Tests for deprecated functionality.
// All cases must have links to the relevant GitHub issues.
