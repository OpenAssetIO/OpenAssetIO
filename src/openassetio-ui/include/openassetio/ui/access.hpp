// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <type_traits>

#include <openassetio/export.h>
#include <openassetio/internal.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Access modes available for UI operations.
 */
namespace ui::access {
/**
 * Access pattern for a @ref glossary_UI_Delegate request.
 */
// NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
enum class UIAccess : std::underlying_type_t<internal::access::Access> {
  /**
   * Used to request a UI element for viewing existing entities.
   *
   * For example, this could be a browser for selecting an existing
   * entity; or a panel providing additional information on a given
   * entity.
   */
  kRead = internal::access::Access::kRead,
  /**
   * Used to request a UI element as part of a publishing workflow.
   *
   * For example, this could be a panel for augmenting @ref trait
   * "traits" that are used by the host in the publishing process, or
   * published in addition to those derived by the host.
   */
  kWrite = internal::access::Access::kWrite,
  /**
   * Used to request a UI element as part of a publishing workflow,
   * where the published data is related to, but not the same as, a
   * given entity.
   *
   * For example, the host could be publishing an organisational unit
   * akin to a "folder", and wishes to communicate that a child folder
   * should be created, rather than versioning up an existing one.
   */
  kCreateRelated = internal::access::Access::kCreateRelated,
};
}  // namespace ui::access
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
