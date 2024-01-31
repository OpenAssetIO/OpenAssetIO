// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Contains private internal implementation details.
 */
namespace internal {
namespace access {
/**
 * Common constant values for strong enumerations of access pattern.
 *
 * We must ensure correspondence between the values of the various
 * workflows' strong enums. This allows for comparison, string lookup,
 * simplifies serialisation, and supports language (especially C)
 * bindings.
 */
enum Access : std::size_t { kRead = 0, kWrite, kCreateRelated, kRequired, kManagerDriven };
}  // namespace access

namespace capability::manager {
/**
 * Common constant values for strong enumerations of capability sets.
 *
 * We must ensure correspondence between the values of the middleware
 * and manager implementation's strong enums. This allows for
 * comparison, string lookup, simplifies serialisation, and supports
 * language (especially C) bindings.
 */
enum Capability : std::size_t {
  kEntityReferenceIdentification = 0,
  kManagementPolicyQueries,
  kStatefulContexts,
  kCustomTerminology,
  kResolution,
  kPublishing,
  kRelationshipQueries,
  kExistenceQueries,
  kDefaultEntityReferences,
  kEntityTraitIntrospection
};
}  // namespace capability::manager

}  // namespace internal
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
