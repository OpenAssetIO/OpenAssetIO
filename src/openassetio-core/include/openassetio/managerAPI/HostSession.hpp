// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/managerAPI/Host.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerAPI {
/**
 * The HostSession is a manager-facing class that represents a discrete
 * API session started by a @ref host in order to communicate with a
 * manager.
 *
 * Any generalised API interactions a Manager may wish to make with a
 * Host should be performed through the HostSession instance supplied
 * with any ManagerInterface entrypoint. These objects should not be
 * directly constructed, cached or otherwise persisted by a Manager.
 *
 * The HostSession provides access to:
 *   - A concrete instance of the @fqref{managerAPI::Host} "Host",
 *     implemented by the tool or application that initiated the API
 *     session.
 *
 * @see @fqref{managerAPI::Host} "Host"
 *
 * @todo Expose logging mechanism through HostSession
 */
class OPENASSETIO_CORE_EXPORT HostSession {
 public:
  explicit HostSession(HostPtr host);

  /**
   * @return The host that initiated the API session.
   */
  [[nodiscard]] HostPtr host() const;

 private:
  HostPtr host_;
};

}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
