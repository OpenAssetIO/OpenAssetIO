// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <utility>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * EntityReference forms a strongly typed wrapper around arbitrary
 * strings to ensure they have been validated by the target @ref manager
 * before being used as an @ref entity_reference in the various entity
 * related API calls.
 *
 * It can be assumed that if
 * @fqref{hostApi.Manager.isEntityReferenceString}
 * "isEntityReferenceString" is true for a given string, then an
 * EntityReference can be constructed from that string.
 *
 * @warning EntityReferences should not be constructed directly by the
 * @ref host, use the creation methods of the manager instead,
 * @fqref{hostApi.Manager.createEntityReference} "createEntityReference"
 * and @fqref{hostApi.Manager.createEntityReferenceIfValid}
 * "createEntityReferenceIfValid".
 *
 * Note that this does not preclude the possibility of a malformed
 * reference. See
 * @fqref{errors.BatchElementError.ErrorCode.kInvalidEntityReference}
 * "kInvalidEntityReference".
 */
class EntityReference final {
 public:
  /**
   * Constructs an EntityReference around the supplied string.
   */
  explicit EntityReference(Str entityReferenceString)
      : entityReferenceString_(std::move(entityReferenceString)) {}

  /**
   * Compare the contents of this reference with another for equality.
   *
   * @param other Entity refernce to compare against.
   *
   * @return `true` if contents are equal, `false` otherwise.
   */
  bool operator==(const EntityReference& other) const {
    return other.entityReferenceString_ == entityReferenceString_;
  }

  /**
   * @return The string representation of this entity reference.
   */
  [[nodiscard]] const Str& toString() const { return entityReferenceString_; }

 private:
  Str entityReferenceString_;
};

static_assert(std::is_move_constructible_v<EntityReference>);
static_assert(std::is_move_assignable_v<EntityReference>);

/// A list of entity references, used or batch-first functions.
using EntityReferences = std::vector<EntityReference>;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
