// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(managerApi, Host)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(HostSession)

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
 *   - A concrete instance of the @fqref{managerApi.Host} "Host",
 *     implemented by the tool or application that initiated the API
 *     session.
 *   - A concrete instance of the @fqref{log.LoggerInterface}
 *     "LoggerInterface", to be used for all message reporting.
 *
 * @see @fqref{managerApi.Host} "Host"
 * @see @fqref{log.LoggerInterface} "LoggerInterface"
 */
class OPENASSETIO_CORE_EXPORT HostSession final {
 public:
  OPENASSETIO_ALIAS_PTR(HostSession)

  /**
   * Constructs a new HostSession holding the supplied host.
   */
  [[nodiscard]] static HostSessionPtr make(HostPtr host, log::LoggerInterfacePtr logger);

  /**
   * @return The host that initiated the API session.
   */
  [[nodiscard]] const HostPtr& host() const;

  /**
   * @return The logger associated with this session
   */
  [[nodiscard]] const log::LoggerInterfacePtr& logger() const;

 private:
  explicit HostSession(HostPtr host, log::LoggerInterfacePtr logger);
  HostPtr host_;
  log::LoggerInterfacePtr logger_;
};
}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
