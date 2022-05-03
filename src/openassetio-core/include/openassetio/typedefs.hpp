// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <string>

#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
/**
 * @anchor CppPrimitiveTypes
 * @name Primitive Types
 *
 * These types are used throughout OpenAssetIO, especially within
 * dictionary-like types such as @ref specification data or
 * @needsref ManagerInterface::info.
 *
 * OpenAssetIO must be able to bridge disparate platforms, including
 * serialization of data. It is therefore useful to ensure that our core
 * primitive types are as predictable and portable as possible.
 *
 * The following type list aims to standardise on types that share a
 * common binary layout across platforms.
 *
 * This also gives us a single point to change should we need to switch
 * to a different primitive representation in future. Therefore all use
 * of primitive types by OpenAssetIO hosts and plugins should use these
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
/// String value type.
using Str = std::string;

/**
 * @}
 */

template <class T>
using SharedPtr = std::shared_ptr<T>;
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
