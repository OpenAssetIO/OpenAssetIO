// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/managerApi/UIDelegateStateInterface.hpp>

#include <any>
#include <optional>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/trait/collection.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

std::any UIDelegateStateInterface::nativeData() { return {}; }

EntityReferences UIDelegateStateInterface::entityReferences() { return {}; }

trait::TraitsDatas UIDelegateStateInterface::entityTraitsDatas() { return {}; }

std::optional<UIDelegateStateInterface::UpdateRequestCallback>
UIDelegateStateInterface::updateRequestCallback() {
  return {};
}
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
