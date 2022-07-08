// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>
#include <string_view>

#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Storage for enum name lookup array.
 */
template <std::size_t N>
using EnumNames = std::array<std::string_view, N>;
/**
 * Explicit enum type so that name lookups do not require a cast.
 */
using EnumIdx = EnumNames<0>::size_type;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
