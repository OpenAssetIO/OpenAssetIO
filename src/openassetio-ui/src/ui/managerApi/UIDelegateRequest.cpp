// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/managerApi/UIDelegateRequest.hpp>

#include <any>
#include <memory>
#include <optional>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateState.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

UIDelegateRequest::Ptr UIDelegateRequest::make(
    hostApi::UIDelegateRequestInterfacePtr uiDelegateRequestInterface) {
  return std::make_shared<UIDelegateRequest>(
      UIDelegateRequest{std::move(uiDelegateRequestInterface)});
}

UIDelegateRequest::UIDelegateRequest(
    hostApi::UIDelegateRequestInterfacePtr uiDelegateRequestInterface)
    : uiDelegateRequestInterface_{std::move(uiDelegateRequestInterface)} {}

std::any UIDelegateRequest::nativeData() { return uiDelegateRequestInterface_->nativeData(); }

EntityReferences UIDelegateRequest::entityReferences() {
  return uiDelegateRequestInterface_->entityReferences();
}

trait::TraitsDatas UIDelegateRequest::entityTraitsDatas() {
  return uiDelegateRequestInterface_->entityTraitsDatas();
}

std::optional<UIDelegateRequest::StateChangedCallback> UIDelegateRequest::stateChangedCallback() {
  auto maybeInterfaceCallback = uiDelegateRequestInterface_->stateChangedCallback();
  // Chain along unset callback.
  if (!maybeInterfaceCallback.has_value()) {
    return {};
  }

  auto interfaceCallback = std::move(*maybeInterfaceCallback);
  // An empty callback (default-constructed std::function) is invalid.
  if (!interfaceCallback) {
    throw errors::InputValidationException{"Callback is undefined."};
  }

  return [interfaceCallback = std::move(interfaceCallback)](UIDelegateStateInterfacePtr newState) {
    if (newState == nullptr) {
      throw errors::InputValidationException{"Cannot call callback with null state."};
    }
    interfaceCallback(hostApi::UIDelegateState::make(std::move(newState)));
  };
}
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
