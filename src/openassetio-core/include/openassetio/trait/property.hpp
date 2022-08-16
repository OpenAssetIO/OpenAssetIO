// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Typedefs for the trait property data stored within specifications.
 */
#pragma once

#include <string>
#include <variant>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Comprises concrete trait views wrapping @ref TraitsData
 * instances.
 */
namespace trait {

/**
 * Type aliases for @ref trait properties within a @ref TraitsData
 * instance.
 */
namespace property {

/**
 * Property dictionary keys
 *
 * Keys must be UTF-8 compatible strings for required portability.
 *
 * Note that typically @ref TraitBase "trait views" will be used to
 * access properties in a @ref TraitsData instance via concrete member
 * functions, so it is highly desirable that keys are ASCII to maximise
 * portability when mapping property keys to member function names.
 */
using Key = std::string;
/// Property dictionary values.
using Value = std::variant<Bool, Int, Float, std::string>;
}  // namespace property

/**
 * Trait unique ID type.
 *
 * IDs must be UTF-8 compatible strings for required portability.
 *
 * Note that typically @ref TraitBase "trait views" will be used to
 * access properties within a @ref TraitsData instance,
 * rather than direct property access using a `TraitId`, so it is
 * desirable that trait IDs are ASCII to maximise portability when
 * mapping IDs to class names.
 */
using TraitId = property::Key;

/// Status of a trait property within a specification.
enum class TraitPropertyStatus { kFound, kMissing, kInvalidValue };
}  // namespace trait
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
