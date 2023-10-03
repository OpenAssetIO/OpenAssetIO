// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

// Deprecated: https://github.com/OpenAssetIO/OpenAssetIO/issues/1127

#include <openassetio/trait/TraitsData.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
// 'typedef' allows attributes, 'using' does not
[[deprecated("Moved to 'trait' namespace")]] typedef trait::TraitsData TraitsData;        // NOLINT
[[deprecated("Moved to 'trait' namespace")]] typedef trait::TraitsDataPtr TraitsDataPtr;  // NOLINT
// NOLINTEND
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
