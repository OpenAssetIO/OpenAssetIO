// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>

#include <any>
#include <optional>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/trait/collection.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

std::any UIDelegateRequestInterface::nativeData() { return {}; }

EntityReferences UIDelegateRequestInterface::entityReferences() { return {}; }

trait::TraitsDatas UIDelegateRequestInterface::entityTraitsDatas() { return {}; }

std::optional<UIDelegateRequestInterface::StateChangedCallback>
UIDelegateRequestInterface::stateChangedCallback() {
  return {};
}

}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
