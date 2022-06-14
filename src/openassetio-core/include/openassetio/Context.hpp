// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>

#include <openassetio/export.h>
#include <openassetio/TraitsData.hpp>
#include <openassetio/managerAPI/ManagerStateBase.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
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
 *  use @ref openassetio.hostAPI.Manager.Manager.createContext or @ref
 *  openassetio.hostAPI.Manager.Manager.createChildContext. A Manager
 *  implementation should never need to create a context of it's own,
 *  one will always be supplied through the ManagerInterface entry
 *  points.
 */
struct Context final {
  /**
   * Storage for enum name lookup array.
   */
  template <std::size_t N>
  using EnumNames = std::array<std::string_view, N>;
  /**
   * Explicit enum type so that name lookups do not require a cast.
   */
  using EnumIdx = EnumNames<0>::size_type;

  /**
   * @name Access Pattern
   */
  enum Access : EnumIdx { kRead, kReadMultiple, kWrite, kWriteMultiple, kUnknown };

  static constexpr EnumNames<5> kAccessNames{"read", "readMultiple", "write", "writeMultiple",
                                             "unknown"};
  /// @}

  /**
   * @name Data Retention
   */
  enum Retention : EnumIdx {
    /// Data will not be used
    kIgnored,
    /// Data will be re-used during a particular action
    kTransient,
    /// Data will be stored and re-used for the session
    kSession,
    /// Data will be permanently stored in the document
    kPermanent
  };

  static constexpr EnumNames<4> kRetentionNames{"ignored", "transient", "session", "permanent"};
  /// @}

  /**
   * Describes what the @ref host is intending to do with the data.
   *
   * For example, when passed to resolve, it specifies if the @ref
   * host is about to read or write. When configuring a BrowserWidget,
   * then it will hint as to whether the Host is wanting to choose a
   * new file name to save, or open an existing one.
   */
  Access access{kUnknown};

  /**
   * A concession to the fact that it's not always possible to fully
   * implement the spec of this API within a @ref host.
   *
   * For example, @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.register
   * "Manager.register()" can return an @ref entity_reference that
   * points to the newly published @ref entity. This is often not the
   * same as the reference that was passed to the call. The Host is
   * expected to store this new reference for future use. For example
   * in the case of a Scene File added to an 'open recent' menu. A
   * Manager may rely on this to ensure a reference that points to a
   * specific version is used in the future.
   *
   * In some cases - such as batch rendering of an image sequence,
   * it may not be possible to store this final reference, due to
   * constraints of the distributed natured of such a render.
   * Often, it is not actually of consequence. To allow the @ref manager
   * to handle these situations correctly, Hosts are required to set
   * this property to reflect their ability to persist this information.
   */
  Retention retention{kTransient};

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
  TraitsDataPtr locale{};

  /**
   * The opaque state token owned by the @ref manager, used to
   * correlate all API calls made using this context.
   *
   * @see @ref stable_resolution
   */
  managerAPI::ManagerStateBasePtr managerState{};

  /**
   * @return `true` if the context is any of the 'Read' based access
   * patterns. If the access is unknown (Access::kUnknown), then `false`
   * is returned.
   */
  [[nodiscard]] inline bool isForRead() const {
    return access == kRead || access == kReadMultiple;
  }

  /**
   * @return `true` if the context is any of the 'Write' based access
   * patterns. If the access is unknown (Access::kUnknown), then `false`
   * is returned.
   */
  [[nodiscard]] inline bool isForWrite() const {
    return access == kWrite || access == kWriteMultiple;
  }

  /**
   * @return `true` if the context is any of the 'Multiple' based access
   * patterns. If the access is unknown (Access::kUnknown), then `false`
   * is returned.
   */
  [[nodiscard]] inline bool isForMultiple() const {
    return access == kReadMultiple || access == kWriteMultiple;
  }
};

using ContextPtr = openassetio::SharedPtr<Context>;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
