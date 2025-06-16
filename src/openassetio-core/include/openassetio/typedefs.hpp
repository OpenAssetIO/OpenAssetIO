// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/macros.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * @anchor CppPrimitiveTypes
 * @name Primitive Types
 *
 * These types are used throughout OpenAssetIO, especially within
 * dictionary-like types such as @fqref{trait.TraitsData} "TraitsData"
 * or @fqref{InfoDictionary} "InfoDictionary".
 *
 * OpenAssetIO must be able to bridge disparate platforms, including
 * serialization of data. It is therefore useful to ensure that our core
 * primitive types are as predictable and portable as possible.
 *
 * The following type list aims to standardise on types that share a
 * common binary layout across platforms.
 *
 * This also gives us a single point to change should we need to switch
 * to a different primitive representation in future, or to switch
 * conditionally for a particular platform. Therefore all use of
 * primitive types by OpenAssetIO hosts and plugins should use these
 * typedefs where possible, to reduce potential find-and-replace pain
 * later.
 *
 * @{
 */
/// Boolean value type.
using Bool = bool;
/// Integer value type.
using Int = int64_t;
/// Real value type.
using Float = double;
/**
 * String value type.
 *
 * This type is guaranteed to be API compatible with `std::string`.
 */
using Str = std::string;

/**
 * Map/Dict of string to string.
 */
using StrMap = std::unordered_map<Str, Str>;

/**
 * @}
 */

/**
 * @name Identifiers
 *
 * Both @ref host "hosts" and @ref manager "managers" must have a
 * unique identifier. The following aliases ensure that a consistent
 * type is used for these identifiers, and allows semantic documentation
 * of an identifier as a parameter/return type.
 *
 * @{
 */

/// A @ref host or @ref manager identifier.
using Identifier = Str;

/// A list of identifiers.
using Identifiers = std::vector<Identifier>;

/**
 * @}
 */
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
