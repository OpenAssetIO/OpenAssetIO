// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>
#include <memory>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(trait, TraitsData)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerStateBase)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
OPENASSETIO_DECLARE_PTR(Context)

/**
 * The Context object is used to convey information about the calling
 * environment to a @ref manager.
 *
 * It holds additional information about the @ref host that may be
 * useful to the @ref manager. Optionally, it holds arbitrary, opaque
 * (to the host), serializable manager state, which can be used by the
 * manager plugin to tie together related calls.
 *
 * A Manager will also use this information to ensure it presents the
 * correct UI, or behavior.
 *
 * The Context is passed to many calls in this API, and it may, or may
 * not need to be used directly.
 *
 * @warning Contexts should never be directly constructed. Hosts should
 * use @fqref{hostApi.Manager.createContext} "createContext" or
 * @fqref{hostApi.Manager.createChildContext} "createChildContext". A
 * Manager implementation should never need to create a context of it's
 * own, one will always be supplied through the ManagerInterface entry
 * points.
 */
class OPENASSETIO_CORE_EXPORT Context final {
 public:
  OPENASSETIO_ALIAS_PTR(Context)

  /**
   * In many situations, the @ref trait_set of the desired @ref entity
   * itself is not entirely sufficient information to realize many
   * functions that a @ref manager wishes to implement. For example,
   * when determining the final file path for an Image that is about
   * to be published - knowing it came from a render catalog, rather
   * than a 'Write node' from a comp tree could result in different
   * behavior.
   *
   * The Locale uses a @fqref{trait.TraitsData} "TraitsData" to describe in
   * more detail, what specific part of a @ref host is requesting an
   * action. In the case of a file browser for example, it may also
   * include information such as whether or not multi-selection is
   * required.
   */
  trait::TraitsDataPtr locale;

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
  [[nodiscard]] static ContextPtr make(trait::TraitsDataPtr locale = nullptr,
                                       managerApi::ManagerStateBasePtr managerState = nullptr);

 private:
  Context(trait::TraitsDataPtr locale, managerApi::ManagerStateBasePtr managerState);
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
