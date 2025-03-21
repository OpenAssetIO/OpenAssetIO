// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>

#include <openassetio/errors/exceptions.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

UIDelegateInterface::UIDelegateInterface() = default;

InfoDictionary UIDelegateInterface::info() { return {}; }

InfoDictionary UIDelegateInterface::settings([[maybe_unused]] const HostSessionPtr& hostSession) {
  return {};
}

// NOLINTNEXTLINE(performance-unnecessary-value-param)
void UIDelegateInterface::initialize(InfoDictionary uiDelegateSettings,
                                     [[maybe_unused]] const HostSessionPtr& hostSession) {
  if (!uiDelegateSettings.empty()) {
    throw errors::InputValidationException{
        "Settings provided but are not supported. The initialize method has not been implemented "
        "by the UI delegate."};
  }
}

}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
