// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <memory>

#include <openassetio/export.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>
#include <trompeloeil.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/ui/access.hpp>
#include <openassetio/ui/hostApi/UIDelegate.hpp>
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {
struct MockHostInterface final : trompeloeil::mock_interface<hostApi::HostInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK0(info);
};

struct MockLoggerInterface final : trompeloeil::mock_interface<log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};

struct MockUIDelegateRequestInterface final
    : trompeloeil::mock_interface<ui::hostApi::UIDelegateRequestInterface> {
  IMPLEMENT_MOCK0(entityReferences);
  IMPLEMENT_MOCK0(entityTraitsDatas);
  IMPLEMENT_MOCK0(nativeData);
  IMPLEMENT_MOCK0(stateChangedCallback);
};

struct MockUIDelegateInterface final
    : trompeloeil::mock_interface<ui::managerApi::UIDelegateInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK5(populateUI);
};

SCENARIO("UIDelegate middleware validation") {
  GIVEN("a UIDelegate") {
    auto hostSession = managerApi::HostSession::make(
        managerApi::Host::make(std::make_shared<MockHostInterface>()),
        std::make_shared<MockLoggerInterface>());

    auto mockUIDelegateInterface = std::make_shared<MockUIDelegateInterface>();

    auto uiDelegate = ui::hostApi::UIDelegate::make(mockUIDelegateInterface, hostSession);

    AND_GIVEN("valid arguments to populateUI") {
      const auto uiTraits = trait::TraitsData::make();
      const auto uiAccess = ui::access::UIAccess::kRead;
      const auto context = Context::make();
      const ui::hostApi::UIDelegateRequestInterfacePtr uiRequestInterface =
          std::make_shared<MockUIDelegateRequestInterface>();

      AND_GIVEN("UIDelegateInterface.populateUI returns nullptr") {
        using trompeloeil::_;
        REQUIRE_CALL(*mockUIDelegateInterface,
                     populateUI(uiTraits, uiAccess, _, context, hostSession))
            .RETURN(nullptr);

        THEN("populateUI throws exception") {
          CHECK_THROWS_MATCHES(
              uiDelegate->populateUI(uiTraits, uiAccess, uiRequestInterface, context),
              openassetio::errors::InputValidationException,
              Catch::Message("UI delegate state is null."));
        }
      }

      AND_GIVEN("UI request is nullptr") {
        const ui::hostApi::UIDelegateRequestInterfacePtr nullUIRequestInterface;

        THEN("populateUI throws exception") {
          CHECK_THROWS_MATCHES(
              uiDelegate->populateUI(uiTraits, uiAccess, nullUIRequestInterface, context),
              openassetio::errors::InputValidationException,
              Catch::Message("UI delegate request cannot be null."));
        }
      }
    }
  }
}

}  // namespace
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
