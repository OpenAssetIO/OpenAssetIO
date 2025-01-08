// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <memory>
#include <type_traits>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/export.h>  // NOLINT - cpplint
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {

/**
 * Mock implementation of a HostInterface
 */
struct MockHostInterface final : trompeloeil::mock_interface<hostApi::HostInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
};

/**
 * Mock implementation of a LoggerInterface
 */
struct MockLoggerInterface final : trompeloeil::mock_interface<log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};

}  // namespace
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

SCENARIO("HostSession constructor is private") {
  STATIC_REQUIRE_FALSE(std::is_constructible_v<openassetio::managerApi::HostSession,
                                               openassetio::managerApi::HostPtr,
                                               openassetio::log::LoggerInterfacePtr>);
}

SCENARIO("HostSession::logger method returns held pointer by reference") {
  GIVEN("a configured HostSession") {
    const openassetio::managerApi::HostSessionPtr session =
        openassetio::managerApi::HostSession::make(
            openassetio::managerApi::Host::make(
                std::make_shared<openassetio::MockHostInterface>()),
            std::make_shared<openassetio::MockLoggerInterface>());

    WHEN("logger is called multiple times") {
      THEN("returned values are references to the same object") {
        CHECK(&session->logger() == &session->logger());
      }
    }
  }
}

SCENARIO("HostSession::host method returns held pointer by reference") {
  GIVEN("a configured HostSession") {
    const openassetio::managerApi::HostSessionPtr session =
        openassetio::managerApi::HostSession::make(
            openassetio::managerApi::Host::make(
                std::make_shared<openassetio::MockHostInterface>()),
            std::make_shared<openassetio::MockLoggerInterface>());

    WHEN("host is called multiple times") {
      THEN("returned values are references to the same object") {
        CHECK(&session->host() == &session->host());
      }
    }
  }
}
