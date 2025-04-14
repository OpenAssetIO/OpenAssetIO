// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

#include <optional>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/ui/access.hpp>

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

void UIDelegateInterface::close([[maybe_unused]] const HostSessionPtr& hostSession) {}

trait::TraitsDataPtr UIDelegateInterface::uiPolicy(
    [[maybe_unused]] const trait::TraitSet& uiTraitSet, [[maybe_unused]] access::UIAccess uiAccess,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  return trait::TraitsData::make();
}

std::optional<UIDelegateStateInterfacePtr> UIDelegateInterface::populateUI(
    [[maybe_unused]] const trait::TraitsDataConstPtr& uiTraitsData,
    [[maybe_unused]] access::UIAccess uiAccess,
    // NOLINTNEXTLINE(performance-unnecessary-value-param)
    [[maybe_unused]] UIDelegateRequestPtr uiRequest,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  return std::nullopt;
}

}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
