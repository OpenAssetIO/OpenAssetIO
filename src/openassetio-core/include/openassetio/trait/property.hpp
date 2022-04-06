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
inline namespace OPENASSETIO_VERSION {
/**
 * Comprises concrete trait views wrapping specification::Specification
 * instances.
 */
namespace trait {

/**
 * Type aliases for @needsref trait properties within a @ref
 * specification::Specification "Specification"
 */
namespace property {

/**
 * Property dictionary keys
 *
 * Keys must be UTF-8 compatible strings for required portability.
 *
 * Note that typically @ref TraitBase "trait views" will be used to
 * access @ref specification::Specification "Specification" properties
 * via concrete member functions, so it is highly desirable that keys
 * are ASCII to maximise portability when mapping property keys to
 * member function names.
 */
using Key = openassetio::Str;
/// Property dictionary values.
using Value = std::variant<Bool, Int, Float, Str>;
}  // namespace property

/**
 * Trait unique ID type.
 *
 * IDs must be UTF-8 compatible strings for required portability.
 *
 * Note that typically @ref TraitBase "trait views" will be used to
 * access @ref specification::Specification "Specification" properties
 * rather than direct property access using a `TraitId`, so it is
 * desirable that trait IDs are ASCII to maximise portability when
 * mapping IDs to class names.
 */
using TraitId = property::Key;

/// Status of a trait property within a specification.
enum class TraitPropertyStatus { kFound, kMissing, kInvalidValue };
}  // namespace trait
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
