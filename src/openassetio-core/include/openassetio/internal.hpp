// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Contains private internal implementation details.
 */
namespace internal::access {
/**
 * Common constant values for strong enumerations of access pattern.
 *
 * We must ensure correspondence between the values of the various
 * workflows' strong enums. This allows for comparison, string lookup,
 * simplifies serialisation, and supports language (especially C)
 * bindings.
 */
enum Access : std::size_t { kRead = 0, kWrite, kCreateRelated };
}  // namespace internal::access
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
