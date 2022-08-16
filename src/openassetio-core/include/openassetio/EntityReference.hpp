// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <string>
#include <utility>

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
 * @ref host, use the creation methods of the manager instead.
 */
class EntityReference final {
 public:
  /**
   * Constructs an EntityReference around the supplied string.
   */
  explicit EntityReference(std::string entityReferenceString)
      : entityReferenceString_(std::move(entityReferenceString)) {}

  /**
   * @return The string representation of this entity reference.
   */
  [[nodiscard]] const std::string& toString() const { return entityReferenceString_; }

 private:
  std::string entityReferenceString_;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
