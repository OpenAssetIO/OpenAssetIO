// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(ManagerStateBase)

/**
 * An abstract base for all @ref manager_state objects.
 *
 * The manager interface is reentrant by design, and its implementation
 * must be thread-safe. The state for a session is held in a separate
 * object, whose lifetime is managed by the host. The state object is
 * considered opaque by the rest of the API, and the manager is free to
 * implement this however desired. This class forms an abstract base
 * whose type is used as a value-type to allow instances of any given
 * managers state to be passed through the various language bindings and
 * API middleware.
 *
 * @see @ref stable_resolution
 * @see @ref manager_state
 */
class ManagerStateBase {
 public:
  OPENASSETIO_ALIAS_PTR(ManagerStateBase)

  virtual ~ManagerStateBase() = default;
};
}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
