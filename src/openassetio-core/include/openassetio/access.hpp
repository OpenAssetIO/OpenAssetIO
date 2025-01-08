// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once

#include <array>
#include <type_traits>

#include <openassetio/export.h>
#include <openassetio/internal.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Access modes available for API operations.
 */
namespace access {

/// Mapping of access enum value to human-readable name.
[[maybe_unused]] constexpr std::array kAccessNames{"read", "write", "createRelated", "required",
                                                   "managerDriven"};

/**
 * Access pattern for a manager policy query.
 *
 * Since @fqref{hostApi.Manager.managementPolicy}
 * "Manager.managementPolicy" /
 * @fqref{managerApi.ManagerInterface.managementPolicy}
 * "ManagerInterface.managementPolicy" is used to determine which
 * functionality is supported by a manager, these constants largely
 * mirror those for the relevant API methods.
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class PolicyAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Host intends to read data.
   *
   * @see @ref ResolveAccess.kRead / @ref RelationsAccess.kRead
   */
  kRead = internal::access::Access::kRead,
  /**
   * Host intends to write data.
   *
   * @see @ref PublishingAccess.kWrite / @ref RelationsAccess.kWrite
   */
  kWrite = internal::access::Access::kWrite,
  /**
   * Hosts intends to write data for a new entity in relation to
   * another.
   *
   * @see @ref PublishingAccess.kCreateRelated /
   * @ref RelationsAccess.kCreateRelated
   */
  kCreateRelated = internal::access::Access::kCreateRelated,
  /**
   * Host wishes to know which subset of traits must have their required
   * properties filled for successful publishing of an entity.
   *
   * Traits are used for both classification of an entity, and
   * communication of properties of that entity. That is, many traits
   * have properties associated with them. When publishing an entity,
   * the entire trait set of that entity must be provided, in order for
   * the manager classify the entity being published. However, it may
   * well be that not all of the properties of those traits need to be
   * set, in order for publishing to succeed.
   *
   * On an individual trait level, some properties will be required and
   * some optional. Determining this currently requires manual
   * inspection of the documentation for that trait.
   *
   * The `kRequired` policy of a manager, with respect to a given entity
   * trait set, refers to the subset of traits that must have their
   * required properties set by the host, in order for publishing to
   * succeed.
   */
  kRequired = internal::access::Access::kRequired,
  /**
   * Host wishes to know the subset of traits that have properties the
   * manager can provide for creating new content when publishing an
   * entity.
   *
   * Note that if a manager provides a property for the host to use
   * during publishing, the host should not assume that the manager
   * "remembers" that it provided that property. I.e. the manager-driven
   * property should be published with the rest of the data, especially
   * if the associated trait is is part of the @ref
   * PolicyAccess.kRequired "kRequired" policy for the entity's trait
   * set.
   *
   * @see @ref ResolveAccess.kManagerDriven
   */
  kManagerDriven = internal::access::Access::kManagerDriven,
};

/**
 * Access pattern for @ref glossary_resolve "entity resolution".
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class ResolveAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Used to query an existing entity for information.
   *
   * For example, trait property values may be used to control the
   * loading of data from a resource, and its subsequent interpretation.
   */
  kRead = internal::access::Access::kRead,
  /**
   * Used by hosts to ask the manager how or where to write new data
   * for an entity.
   *
   * For example, trait property values may be used to control the
   * writing of data to a resource, and specifics of its format or
   * content.
   */
  kManagerDriven = internal::access::Access::kManagerDriven,
};

/**
 * Access pattern for entity trait set queries.
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class EntityTraitsAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Used to query the full trait set of an existing entity.
   *
   * For example, when an entity is known to exist, but is of unknown
   * classification.
   */
  kRead = internal::access::Access::kRead,
  /**
   * Used to query the minimal trait set that must be specified when
   * publishing to a particular entity reference.
   *
   * For example, when validating that a user-supplied entity reference
   * is appropriate for a publishing operation.
   */
  kWrite = internal::access::Access::kWrite,
};

/**
 * Access pattern for @ref publish "publishing".
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class PublishingAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Used whenever the entity reference explicitly targets the specific
   * entity whose data is being written.
   *
   * For example creating or updating a simple, unstructured asset such
   * as an image or other file-based data.
   *
   * Hosts should also choose this access mode if unsure which access
   * mode is appropriate.
   */
  kWrite = internal::access::Access::kWrite,
  /**
   * Used whenever the entity reference points to an existing entity,
   * and the intention is to create a  new, related entity instead of
   * updating the target.
   *
   * For example, when programmatically creating new  entities under an
   * existing parent collection, or the publishing of the components of
   * a structured asset based on a single root entity reference.
   */
  kCreateRelated = internal::access::Access::kCreateRelated,
};

/**
 * Access pattern for a relationship query.
 *
 * @see @fqref{hostApi.Manager.getWithRelationship}
 * "Manager.getWithRelationship" /
 * @fqref{managerApi.ManagerInterface.getWithRelationship}
 * "ManagerInterface.getWithRelationship" (and similar).
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class RelationsAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Used to retrieve references to pre-existing related entities.
   */
  kRead = internal::access::Access::kRead,
  /**
   * Used to retrieve references to related entities, with the intention
   * of writing data to them.
   *
   * For example, during a @ref publish this could be used to retrieve
   * references to the individual components of an entity, allowing the
   * host to ask the manager for details on how and where to update
   * them.
   *
   * This access mode should be used when the related entity already
   * exists, or where the host is unsure whether it exists or not.
   * Otherwise see @ref RelationsAccess.kCreateRelated
   */
  kWrite = internal::access::Access::kWrite,
  /**
   * Used to allow the manager to dictate a list of entities that the
   * host should create.
   *
   * For example, during a @ref publish this could be used to decompose
   * a single entity reference into a list of entity references, one for
   * each component that the manager expects to be published, each with
   * a different target location on disk.
   *
   * For querying pre-existing related entities, with the intention of
   * writing new data, see @ref RelationsAccess.kWrite.
   */
  kCreateRelated = internal::access::Access::kCreateRelated,
};

/**
 * Access pattern when querying a sensible default starting entity for
 * further queries.
 *
 * @see @fqref{hostApi.Manager.defaultEntityReference}
 * "Manager.defaultEntityReference" /
 * @fqref{managerApi.ManagerInterface.defaultEntityReference}
 * "ManagerInterface.defaultEntityReference",
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class DefaultEntityAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Indicate that the @ref manager should provide an entity reference
   * that can be queried for existing data.
   *
   * @see @ref ResolveAccess.kRead, @ref RelationsAccess.kRead
   */
  kRead = internal::access::Access::kRead,

  /**
   * Indicate that the @ref manager should provide a reference suitable
   * for publishing to.
   *
   * @see @ref PublishingAccess.kWrite,
   * @ref RelationsAccess.kWrite
   */
  kWrite = internal::access::Access::kWrite,

  /**
   * Indicate that the @ref manager should provide an entity reference
   * that will be used to @ref publish one or more new entities to.
   *
   * @see @ref PublishingAccess.kCreateRelated,
   * @ref RelationsAccess.kCreateRelated
   */
  kCreateRelated = internal::access::Access::kCreateRelated
};
}  // namespace access
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
