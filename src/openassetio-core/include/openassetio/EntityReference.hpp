// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
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
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if contents are equal, `false` otherwise.
   */
  [[nodiscard]] bool operator==(const EntityReference& other) const {
    return other.entityReferenceString_ == entityReferenceString_;
  }

  /**
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if contents are not equal, `false` otherwise.
   */
  [[nodiscard]] bool operator!=(const EntityReference& other) const { return !(*this == other); }

  /**
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if this reference is less than other, `false`
   * otherwise.
   */
  [[nodiscard]] bool operator<(const EntityReference& other) const {
    return entityReferenceString_ < other.entityReferenceString_;
  }

  /**
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if this reference is less or equal than other,
   * `false` otherwise.
   */
  [[nodiscard]] bool operator<=(const EntityReference& other) const {
    return entityReferenceString_ <= other.entityReferenceString_;
  }

  /**
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if this reference is greater than other, `false`
   * otherwise.
   */
  [[nodiscard]] bool operator>(const EntityReference& other) const { return !(*this <= other); }

  /**
   * Compare this reference with another lexicographically.
   *
   * @param other Entity reference to compare against.
   *
   * @return `true` if this reference is greater or equal than other,
   * `false` otherwise.
   */
  [[nodiscard]] bool operator>=(const EntityReference& other) const { return !(*this < other); }
  /**
   * @return The string representation of this entity reference.
   */
  [[nodiscard]] const Str& toString() const { return entityReferenceString_; }

 private:
  Str entityReferenceString_;
};

static_assert(std::is_move_constructible_v<EntityReference>);
static_assert(std::is_move_assignable_v<EntityReference>);
static_assert(std::is_copy_constructible_v<EntityReference>);
static_assert(std::is_copy_assignable_v<EntityReference>);

/// A list of entity references, used or batch-first functions.
using EntityReferences = std::vector<EntityReference>;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

namespace std {
template <>
struct hash<openassetio::EntityReference> {
  std::size_t operator()(const openassetio::EntityReference& ref) const noexcept {
    // Construct hash using common hashing function found
    // across the literature, e.g. boost::hash_combine. I.e.
    // seed ^= hasher(value) + 0x9e3779b9 + (seed << 6) + (seed >> 2);

    // int(2^32 / phi) (where phi is the golden ratio).
    constexpr std::size_t kInvPhi = 0x9e3779b9;
    // Small coprime shift distances to spread out the bits.
    constexpr std::size_t kLShift = 6;
    constexpr std::size_t kRShift = 2;
    // Seed incorporating type hash, assuming initial seed of 0
    // (note: hash_code() is not constexpr in C++17).
    static const std::size_t kSeed = typeid(openassetio::EntityReference).hash_code() + kInvPhi;
    // Precompute rhs of hash equation.
    static const std::size_t kBitMixer = kInvPhi + (kSeed << kLShift) + (kSeed >> kRShift);

    return kSeed ^ (std::hash<openassetio::Str>{}(ref.toString()) + kBitMixer);
  }
};
}  // namespace std
