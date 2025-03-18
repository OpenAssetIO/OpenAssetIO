// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
/**
 * Tests for the C++ specifics of the UIDelegateRequest/State[Interface]
 * classes.
 *
 * See Python tests for more complete coverage.
 */
#include <any>
#include <functional>
#include <memory>
#include <optional>
#include <utility>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/EntityReference.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateState.hpp>
#include <openassetio/ui/managerApi/UIDelegateRequest.hpp>
#include <openassetio/ui/managerApi/UIDelegateStateInterface.hpp>

using openassetio::ui::hostApi::UIDelegateRequestInterface;
using openassetio::ui::hostApi::UIDelegateState;
using openassetio::ui::managerApi::UIDelegateRequest;
using openassetio::ui::managerApi::UIDelegateStateInterface;

SCENARIO("Default values passed through middleware") {
  GIVEN("a default request") {
    auto request = UIDelegateRequest::make(std::make_shared<UIDelegateRequestInterface>());

    WHEN("values are extracted") {
      const openassetio::EntityReferences entityReferences = request->entityReferences();
      const openassetio::trait::TraitsDatas traitsDatas = request->entityTraitsDatas();
      const std::any nativeData = request->nativeData();
      const std::optional<UIDelegateRequest::StateChangedCallback> stateChangedCallback =
          request->stateChangedCallback();

      THEN("values have the expected defaults") {
        CHECK(entityReferences.empty());
        CHECK(traitsDatas.empty());
        CHECK(!nativeData.has_value());
        CHECK(!stateChangedCallback.has_value());
      }
    }
  }

  GIVEN("a default state") {
    auto state = UIDelegateState::make(std::make_shared<UIDelegateStateInterface>());

    WHEN("values are extracted") {
      const openassetio::EntityReferences entityReferences = state->entityReferences();
      const openassetio::trait::TraitsDatas traitsDatas = state->entityTraitsDatas();
      const std::any nativeData = state->nativeData();
      const std::optional<UIDelegateState::UpdateRequestCallback> updateRequestCallback =
          state->updateRequestCallback();

      THEN("values have the expected defaults") {
        CHECK(entityReferences.empty());
        CHECK(traitsDatas.empty());
        CHECK(!nativeData.has_value());
        CHECK(!updateRequestCallback.has_value());
      }
    }
  }
}

namespace {

struct RequestImplWithCallback : UIDelegateRequestInterface {
  std::optional<UIDelegateRequestInterface::StateChangedCallback> stateChangedCallback() override {
    // NOLINTNEXTLINE(performance-unnecessary-value-param)
    return []([[maybe_unused]] std::optional<UIDelegateState::Ptr> state) {};
  }
};

struct StateImplWithCallback : UIDelegateStateInterface {
  MAKE_MOCK1(mockCallback, void(std::optional<UIDelegateRequest::Ptr>));

  std::optional<UIDelegateStateInterface::UpdateRequestCallback> updateRequestCallback() override {
    return [this](std::optional<UIDelegateRequest::Ptr> request) {
      mockCallback(std::move(request));
    };
  }
};
}  // namespace

SCENARIO("Attempting nullptrs in callbacks") {
  GIVEN("a request with a state change callback") {
    auto request = UIDelegateRequest::make(std::make_shared<RequestImplWithCallback>());

    THEN("passing a nullptr state throws exception") {
      // NOLINTNEXTLINE(bugprone-unchecked-optional-access)
      auto callback = request->stateChangedCallback().value();

      CHECK_THROWS_MATCHES(callback(nullptr), openassetio::errors::InputValidationException,
                           Catch::Message("Cannot call callback with null state."));
    }
  }

  GIVEN("a state with a request update callback") {
    auto stateImpl = std::make_shared<StateImplWithCallback>();
    auto state = UIDelegateState::make(stateImpl);

    // NOLINTNEXTLINE(bugprone-unchecked-optional-access)
    auto callback = state->updateRequestCallback().value();

    THEN("passing a nullptr request throws exception") {
      CHECK_THROWS_MATCHES(
          callback(nullptr), openassetio::errors::InputValidationException,
          Catch::Message("Cannot call callback with nullptr request, use std::nullopt instead."));
    }

    THEN("passing a nullopt request is accepted") {
      REQUIRE_CALL(*stateImpl, mockCallback(std::nullopt));
      callback(std::nullopt);
    }
  }
}

namespace {

struct RequestImplWithBlankCallback : UIDelegateRequestInterface {
  std::optional<UIDelegateRequestInterface::StateChangedCallback> stateChangedCallback() override {
    return UIDelegateRequestInterface::StateChangedCallback{};
  }
};

struct StateImplWithBlankCallback : UIDelegateStateInterface {
  std::optional<UIDelegateStateInterface::UpdateRequestCallback> updateRequestCallback() override {
    return UIDelegateStateInterface::UpdateRequestCallback{};
  }
};
}  // namespace

SCENARIO("Attempting to use default-constructed std::function as a callback") {
  GIVEN("a request with an invalid state change callback") {
    auto request = UIDelegateRequest::make(std::make_shared<RequestImplWithBlankCallback>());

    THEN("retrieving callback throws exception") {
      CHECK_THROWS_MATCHES(request->stateChangedCallback(),
                           openassetio::errors::InputValidationException,
                           Catch::Message("Callback is undefined."));
    }
  }

  GIVEN("a state with an invalid request update callback") {
    auto state = UIDelegateState::make(std::make_shared<StateImplWithBlankCallback>());

    THEN("retrieving callback throws exception") {
      CHECK_THROWS_MATCHES(state->updateRequestCallback(),
                           openassetio::errors::InputValidationException,
                           Catch::Message("Callback is undefined."));
    }
  }
}
