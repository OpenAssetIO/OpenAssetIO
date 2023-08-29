// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <array>

#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Access modes available for API operations.
 */
namespace access {

/**
 * Common constant values for strong enumerations.
 *
 * We must ensure correspondence between the values of the various
 * workflows' strong enums. This allows for comparison, string lookup,
 * simplifies serialisation, and supports language (especially C)
 * bindings.
 */
enum Access { kRead = 0, kWrite, kCreateRelated };

/// Mapping of access enum value to human-readable name.
[[maybe_unused]] constexpr std::array kAccessNames{"read", "write", "createRelated"};

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
enum class PolicyAccess : int {
  /**
   * Host intends to read data.
   *
   * @see @ref ResolveAccess.kRead / @ref RelationsAccess.kRead
   */
  kRead = kRead,
  /**
   * Host intends to write data.
   *
   * @see @ref PublishingAccess.kWrite / @ref RelationsAccess.kWrite
   */
  kWrite = kWrite,
  /**
   * Hosts intends to write data for a new entity in relation to
   * another.
   *
   * @see @ref PublishingAccess.kCreateRelated /
   * @ref RelationsAccess.kCreateRelated
   */
  kCreateRelated = kCreateRelated,
};

/**
 * Access pattern for @ref glossary_resolve "entity resolution".
 */
enum class ResolveAccess : int {
  /**
   * Used to query an existing entity for information.
   *
   * For example, trait property values may be used to control the
   * loading of data from a resource, and its subsequent interpretation.
   */
  kRead = kRead,
  /**
   * Used by hosts to ask the manager how or where to write new data
   * for an entity.
   *
   * For example, trait property values may be used to control the
   * writing of data to a resource, and specifics of its format or
   * content.
   */
  kWrite = kWrite,
};

/**
 * Access pattern for @ref publish "publishing".
 */
enum class PublishingAccess : int {
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
  kWrite = kWrite,
  /**
   * Used whenever the entity reference points to an existing entity,
   * and the intention is to create a  new, related entity instead of
   * updating the target.
   *
   * For example, when programmatically creating new  entities under an
   * existing parent collection, or the publishing of the components of
   * a structured asset based on a single root entity reference.
   */
  kCreateRelated = kCreateRelated,
};

/**
 * Access pattern for a relationship query.
 *
 * @see @fqref{hostApi.Manager.getWithRelationship}
 * "Manager.getWithRelationship" /
 * @fqref{managerApi.ManagerInterface.getWithRelationship}
 * "ManagerInterface.getWithRelationship" (and similar).
 */
enum class RelationsAccess : int {
  /**
   * Used to retrieve references to pre-existing related entities.
   */
  kRead = kRead,
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
   * Otherwise see @ref kCreateRelated
   */
  kWrite = kWrite,
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
   * writing new data, see @ref kWrite.
   */
  kCreateRelated = kCreateRelated,
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
enum class DefaultEntityAccess : int {
  /**
   * Indicate that the @ref manager should provide an entity reference
   * that can be queried for existing data.
   *
   * @see @ref ResolveAccess.kRead, @ref RelationsAccess.kRead
   */
  kRead = kRead,

  /**
   * Indicate that the @ref manager should provide a reference suitable
   * for publishing to.
   *
   * @see @ref PublishingAccess.kWrite,
   * @ref RelationsAccess.kWrite
   */
  kWrite = kWrite,

  /**
   * Indicate that the @ref manager should provide an entity reference
   * that will be used to @ref publish one or more new entities to.
   *
   * @see @ref PublishingAccess.kCreateRelated,
   * @ref RelationsAccess.kCreateRelated
   */
  kCreateRelated = kCreateRelated
};
}  // namespace access
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
