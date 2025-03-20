// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

UIDelegateInterface::UIDelegateInterface() = default;

InfoDictionary UIDelegateInterface::info() { return {}; }
// TODO(DF): fill out details

}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
