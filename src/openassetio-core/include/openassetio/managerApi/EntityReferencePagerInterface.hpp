// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#pragma once

#include <vector>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(Context)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(EntityReferencePagerInterface)

/**
 * Deals with the retrieval of paginated data from the backend at the
 * behest of the host.
 *
 * The manager is expected to extend this type, and store data necessary
 * to perform the paging operations on the extended object, utilizing
 * caching when possible to reduce redundant queries.
 *
 * Thread-safety of operations is not expected. Hosts will synchronize
 * calls themselves, if required.
 *
 * This is a non-copyable object that will be held in a `shared_ptr`,
 * meaning multiple references may be held, but only to a single
 * instance of the ongoing query, whose destructor will be called when
 * all references are released. As such, the destructor of this class is
 * a good place to place any complex cleanup operations (e.g. closing
 * open connections).
 *
 * To support as wide array of possible backends as possible,
 * OpenAssetIO places no restraints on the behaviour of this type
 * concerning performance, however, it is considered friendly to
 * document the performance characteristics of your Pager
 * implementation.
 */
class OPENASSETIO_CORE_EXPORT EntityReferencePagerInterface {
 public:
  OPENASSETIO_ALIAS_PTR(EntityReferencePagerInterface)
  using Page = std::vector<EntityReference>;

  /// Defaulted default constructor.
  EntityReferencePagerInterface() = default;

  /**
   * Deleted copy constructor.
   *
   * Copying of pagers is disallowed, for convenience of implementation.
   *
   * However, be aware that multiple references to the pager may be
   * held.
   */
  explicit EntityReferencePagerInterface(const EntityReferencePagerInterface&) = delete;

  /**
   * Deleted copy assignment operator.
   *
   * Copying of pagers is disallowed, for convenience of implementation.
   *
   * However, be aware that multiple references to the pager may be
   * held.
   */
  EntityReferencePagerInterface& operator=(const EntityReferencePagerInterface&) = delete;

  /// Defaulted move constructor.
  EntityReferencePagerInterface(EntityReferencePagerInterface&&) noexcept = default;

  /// Defaulted move assignment operator.
  EntityReferencePagerInterface& operator=(EntityReferencePagerInterface&&) noexcept = default;

  /**
   * Manager should override destructor to be notified when query has
   * finished.
   */
  virtual ~EntityReferencePagerInterface() = default;

  /**
   * Returns whether or not there is more data accessible by advancing
   * the page.
   *
   * The mechanism to acquire this information is variable, and left up
   * to the specifics of the backend implementation.
   *
   * @return `true` if another page is available, `false` otherwise.
   */
  virtual bool hasNext(const HostSessionPtr&) = 0;

  /**
   * Return the current page of data.
   *
   * If the current page has advanced beyond the last page, an empty
   * list should be returned.
   *
   * @return The current page's list of entity references.
   */
  virtual Page get(const HostSessionPtr&) = 0;

  /**
   * Advance the page.
   *
   * If currently on the last page of results, calling `next` should
   * logically advance to the page after the last page, in analogy with
   * `std::end`. Subsequent calls should then be a no-op. In this state,
   * @ref hasNext should continue to return `false` and @ref get should
   * return an empty page.
   */
  virtual void next(const HostSessionPtr&) = 0;

  /**
   * Close the paging query.
   *
   * Signals that the host is finished with the paging query,
   * allowing for any potential cleanup that may need to be performed.
   * This method is guaranteed to be called only once, and no other
   * interface methods will be called by the host thereafter.
   *
   * This method is called from a destructor. Thrown exceptions will be
   * caught and logged as errors if possible. Despite that, throwing
   * from this function is nonetheless discouraged.
   */
  virtual void close(const HostSessionPtr& hostSession);
};
static_assert(!std::is_copy_constructible_v<EntityReferencePagerInterface>);
static_assert(!std::is_copy_assignable_v<EntityReferencePagerInterface>);

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
