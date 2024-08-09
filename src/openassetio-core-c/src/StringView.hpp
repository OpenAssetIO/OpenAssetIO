// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <algorithm>
#include <cstring>

#include <openassetio/c/StringView.h>
#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Copy a source string to a destination C StringView.
 *
 * If the `dest` has insufficient `capacity` to hold the `src` string,
 * then the string is truncated at `capacity` characters.
 *
 * @param dest Target string.
 * @param src Source string.
 */
inline void assignStringView(oa_StringView* dest, const std::string_view src) {
  dest->size = std::min(src.size(), dest->capacity);
  std::memcpy(dest->data, src.data(), dest->size);
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
