// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/EntityReference.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(managerApi, EntityReferencePagerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

OPENASSETIO_DECLARE_PTR(EntityReferencePager)

/**
 * The EntityReferencePager allows for the retrieval and traversal of
 * large datasets in a paginated manner.
 *
 * @note Instances of this class should not be constructed directly by
 * the host.
 *
 * @see @ref Manager.getWithRelationship
 * @see @ref Manager.getWithRelationships
 *
 * None of the functions of this class should be considered thread-safe.
 * Hosts should add their own synchronization around concurrent usage.
 *
 * Due to the variance of backends, construction, `hasNext`, `get` and
 * `next` may all reasonably need to perform non-trivial, networked
 * operations, and thus performance characteristics should not be
 * assumed.
 *
 * Destruction of this object is a signal to the manager that the
 * connection query is finished. For this reason you should avoid
 * keeping hold of this object for longer than necessary.
 */
class OPENASSETIO_CORE_EXPORT EntityReferencePager final {
 public:
  OPENASSETIO_ALIAS_PTR(EntityReferencePager)
  using Page = EntityReferences;

  /**
   * Constructs a new EntityReferencePager wrapping a @ref manager
   * plugin's implementation.
   *
   * @note Instances of this class should not be constructed
   * directly by the host.
   *
   * @param pagerInterface Implementation of the underlying pager.
   * @param hostSession The API session.
   * @return Newly created instance wrapped in a `std::shared_ptr`.
   */
  [[nodiscard]] static EntityReferencePager::Ptr make(
      managerApi::EntityReferencePagerInterfacePtr pagerInterface,
      managerApi::HostSessionPtr hostSession);

  /**
   * Deleted copy constructor.
   *
   * EntityReferencePager cannot be copied, as each object represents a
   * single paginated query.
   */
  EntityReferencePager(const EntityReferencePager&) = delete;

  /**
   * Deleted copy assignment operator.
   *
   * EntityReferencePager cannot be copied, as each object represents a
   * single paginated query.
   */
  EntityReferencePager& operator=(const EntityReferencePager&) = delete;

  /// Defaulted move constructor.
  EntityReferencePager(EntityReferencePager&&) noexcept = default;

  /// Defaulted move assignment operator.
  EntityReferencePager& operator=(EntityReferencePager&&) noexcept = default;

  /**
   *  Destruction of this object is tantamount to closing the query.
   */
  ~EntityReferencePager();

  /**
   * Return whether or not there is more data accessible by advancing
   * the page.
   *
   * @return `true` if another page is available, `false` otherwise.
   */
  bool hasNext();

  /**
   * Return the current page of data.
   *
   * If the current page has advanced beyond the last page, an empty
   * list will be returned.
   *
   * @return The current page's list of entity references.
   */
  Page get();

  /**
   * Advance the page.
   *
   * Advancing beyond the last page is not an error, but will result in
   * all subsequent calls to @ref get to return an empty page, whilst
   * @ref hasNext will continue to return `false`.
   */
  void next();

 private:
  EntityReferencePager(managerApi::EntityReferencePagerInterfacePtr pagerInterface,
                       managerApi::HostSessionPtr hostSession);

  managerApi::EntityReferencePagerInterfacePtr pagerInterface_;
  managerApi::HostSessionPtr hostSession_;
};
static_assert(!std::is_default_constructible_v<EntityReferencePager>);
static_assert(!std::is_copy_constructible_v<EntityReferencePager>);
static_assert(!std::is_copy_assignable_v<EntityReferencePager>);

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
