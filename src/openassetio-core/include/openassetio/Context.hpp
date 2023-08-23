// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>
#include <memory>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(TraitsData)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerStateBase)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
OPENASSETIO_DECLARE_PTR(Context)

/**
 *  The Context object is used to convey information about the calling
 *  environment to a @ref manager. It encapsulates several key access
 *  properties, as well as providing additional information about the
 *  @ref host that may be useful to the @ref manager.
 *
 *  A Manager will also use this information to ensure it presents the
 *  correct UI, or behavior.
 *
 *  The Context is passed to many calls in this API, and it may, or may
 *  not need to be used directly.
 *
 *  @warning Contexts should never be directly constructed. Hosts should
 *  use @fqref{hostApi.Manager.createContext} "createContext" or
 *  @fqref{hostApi.Manager.createChildContext} "createChildContext". A
 *  Manager implementation should never need to create a context of it's
 *  own, one will always be supplied through the ManagerInterface entry
 *  points.
 */
class OPENASSETIO_CORE_EXPORT Context final {
 public:
  OPENASSETIO_ALIAS_PTR(Context)

  /**
   * @name Access Pattern
   */
  enum class Access {
    /**
     * Host intends to read data. For example, trait property values
     * obtained via `resolve` may be used to control the loading of data
     * from a resource, and its subsequent interpretation.
     */
    kRead,
    /**
     * Host intends to write data.  For example, trait property values
     * obtained via `resolve` may be used to control the writing of data
     * to a resource, and specifics of its format or content. During
     * publishing this must be used whenever the entity reference
     * explicitly targets the specific entity whose data is being
     * written. For example creating or updating a simple, unstructured
     * asset such as an image or other file-based data.
     */
    kWrite,
    /**
     * Hosts intends to write data for a new entity in relation to
     * another. During publishing this must be used whenever the entity
     * reference points to an existing entity, and the intention is to
     * create a  new, related entity instead of updating the target. For
     * example, when programmatically creating new  entities under an
     * existing parent collection, or the publishing of the components
     * of a structured asset based on a single root entity reference.
     */
    kCreateRelated,
    /// Unknown Access Pattern
    kUnknown
  };

  static constexpr std::array kAccessNames{"read", "write", "createRelated", "unknown"};
  /// @}

  /**
   * Describes what the @ref host is intending to do with the data.
   *
   * For example, when passed to resolve, it specifies if the @ref host
   * is about to read or write. When configuring a BrowserWidget, then
   * it will hint as to whether the Host is wanting to choose a new file
   * name to save, or open an existing one.
   *
   * See also @ref create_related "Create related glossary entry".
   */
  Access access;

  /**
   * In many situations, the @ref trait_set of the desired @ref entity
   * itself is not entirely sufficient information to realize many
   * functions that a @ref manager wishes to implement. For example,
   * when determining the final file path for an Image that is about
   * to be published - knowing it came from a render catalog, rather
   * than a 'Write node' from a comp tree could result in different
   * behavior.
   *
   * The Locale uses a @fqref{TraitsData} "TraitsData" to describe in
   * more detail, what specific part of a @ref host is requesting an
   * action. In the case of a file browser for example, it may also
   * include information such as whether or not multi-selection is
   * required.
   */
  TraitsDataPtr locale;

  /**
   * The opaque state token owned by the @ref manager, used to
   * correlate all API calls made using this context.
   *
   * @see @ref stable_resolution
   */
  managerApi::ManagerStateBasePtr managerState;

  /**
   * Constructs a new context.
   *
   * @warning This method should never be called directly by host code -
   * @fqref{hostApi.Manager.createContext} "Manager.createContext"
   * should always be used instead.
   */
  [[nodiscard]] static ContextPtr make(Access access = Access::kUnknown,
                                       TraitsDataPtr locale = nullptr,
                                       managerApi::ManagerStateBasePtr managerState = nullptr);
  /**
   * @return `true` if the context is a 'Read' based access pattern. If
   * the access is unknown (Access::kUnknown), then `false` is returned.
   */
  [[nodiscard]] inline bool isForRead() const { return access == Access::kRead; }

  /**
   * @return `true` if the context is a 'Write' based access pattern. If
   * the access is unknown (Access::kUnknown), then `false` is returned.
   */
  [[nodiscard]] inline bool isForWrite() const {
    return access == Access::kWrite || access == Access::kCreateRelated;
  }

 private:
  Context(Access access, TraitsDataPtr locale, managerApi::ManagerStateBasePtr managerState);
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
