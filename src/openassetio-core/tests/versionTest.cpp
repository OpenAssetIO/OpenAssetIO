// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <catch2/catch.hpp>

#include <openassetio/version.hpp>

SCENARIO("OpenassetIO exposes version information") {
  CHECK(openassetio::majorVersion() == OPENASSETIO_VERSION_MAJOR);
  CHECK(openassetio::minorVersion() == OPENASSETIO_VERSION_MINOR);
  CHECK(openassetio::patchVersion() == OPENASSETIO_VERSION_PATCH);
  CHECK(openassetio::betaMajorVersion() == OPENASSETIO_BETA_VERSION_MAJOR);
  CHECK(openassetio::betaMinorVersion() == OPENASSETIO_BETA_VERSION_MINOR);
  CHECK(openassetio::versionString() == OPENASSETIO_VERSION_STRING);
}
