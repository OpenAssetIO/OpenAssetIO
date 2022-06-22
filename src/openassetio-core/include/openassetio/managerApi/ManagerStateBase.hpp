// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {
/**
 * An abstract base for all @ref manager_state objects.
 *
 * The manager interface is by design stateless, the state for a
 * session is held in a separate object, whose lifetime is managed by
 * the host. The state object is considered opaque by the rest of the
 * API, and the manager is free to implement this however desired. This
 * class forms an abstract base whose type is used as a value-type to
 * allow instances of any given managers state to be passed through the
 * various language bindings and API middleware.
 *
 * @see @ref stable_resolution
 * @see @ref manager_state
 */
struct ManagerStateBase {
  virtual ~ManagerStateBase() = default;
};

using ManagerStateBasePtr = std::shared_ptr<ManagerStateBase>;
}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
