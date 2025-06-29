// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
/**
 * @file
 *
 * Defines common keys for lookup in manager information dictionaries.
 */
#pragma once

#include <string_view>

#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Constants used throughout the OpenAssetIO API.
 */
namespace constants {

/**
 * @name Info dictionary field names.
 *
 * Bare strings should never be used to help protect against
 * inconsistencies and future changes.
 *
 * @{
 */

// General

// NOLINTBEGIN(readability-identifier-naming): requires source breaking change.
inline constexpr std::string_view kInfoKey_SmallIcon = "smallIcon";
inline constexpr std::string_view kInfoKey_Icon = "icon";

/**
 * Indicate that the callee is written primarily in Python.
 *
 * OpenAssetIO is a mostly seamless dual-language library, but for some
 * access patterns it may be necessary for callers to be aware that the
 * callee is written in Python to ensure correct behaviour.
 *
 * @see @ref hostApi.HostInterface.info "HostInterface.info".
 */
inline constexpr std::string_view kInfoKey_IsPython = "isPython";

// Entity Reference Properties

/**
 * Common prefix for all entity references of a particular manager.
 *
 * This field may be used by the API to optimize queries to
 * isEntityReferenceString in situations where bridging languages, etc.
 * can be expensive (particularly in the case of python plug-ins called
 * from multi-threaded C++).
 */
inline constexpr std::string_view kInfoKey_EntityReferencesMatchPrefix =
    "entityReferencesMatchPrefix";

// NOLINTEND(readability-identifier-naming)
/// @}
}  // namespace constants
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
