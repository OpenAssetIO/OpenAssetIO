// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/hostApi/UIDelegateState.hpp>

#include <any>
#include <memory>
#include <optional>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/ui/managerApi/UIDelegateRequest.hpp>
#include <openassetio/ui/managerApi/UIDelegateStateInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

UIDelegateState::Ptr UIDelegateState::make(
    managerApi::UIDelegateStateInterfacePtr uiDelegateStateInterface) {
  return std::make_shared<UIDelegateState>(UIDelegateState{std::move(uiDelegateStateInterface)});
}

UIDelegateState::UIDelegateState(managerApi::UIDelegateStateInterfacePtr uiDelegateStateInterface)
    : uiDelegateStateInterface_{std::move(uiDelegateStateInterface)} {}

std::any UIDelegateState::nativeData() { return uiDelegateStateInterface_->nativeData(); }

EntityReferences UIDelegateState::entityReferences() {
  return uiDelegateStateInterface_->entityReferences();
}

trait::TraitsDatas UIDelegateState::entityTraitsDatas() {
  return uiDelegateStateInterface_->entityTraitsDatas();
}

std::optional<UIDelegateState::UpdateRequestCallback> UIDelegateState::updateRequestCallback() {
  auto maybeInterfaceCallback = uiDelegateStateInterface_->updateRequestCallback();
  // Chain along unset callback.
  if (!maybeInterfaceCallback.has_value()) {
    return {};
  }

  auto interfaceCallback = std::move(*maybeInterfaceCallback);
  // An empty callback (default-constructed std::function) is invalid.
  if (!interfaceCallback) {
    throw errors::InputValidationException{"Callback is undefined."};
  }

  return [interfaceCallback = std::move(interfaceCallback)](
             std::optional<UIDelegateRequestInterfacePtr> newRequest) {
    // Chain along nullopt.
    if (!newRequest.has_value()) {
      interfaceCallback(std::nullopt);
      return;
    }

    // std::optional containing a nullptr is not valid.
    if (*newRequest == nullptr) {
      throw errors::InputValidationException(
          "Cannot call callback with nullptr request, use std::nullopt instead.");
    }

    // Wrap request in middleware and call wrapped callback.
    interfaceCallback(managerApi::UIDelegateRequest::make(std::move(*newRequest)));
  };
}
}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
