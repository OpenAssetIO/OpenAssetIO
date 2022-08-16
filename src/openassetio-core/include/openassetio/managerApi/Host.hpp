// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(Host)

/**
 * The Host object represents the tool or application that created a
 * session with OpenAssetIO, and wants to query or store information
 * within a @ref manager.
 *
 * The Host provides a generalised API to query the identity of the
 * caller of the API. In the future, this interface may be extended to
 * allow retrieval of information about available documents as well as
 * which entities are used within these documents.
 *
 * Hosts should never be directly constructed by the Manager's
 * implementation. Instead, the @ref managerApi.HostSession class
 * provided to all manager API entry points provides access to the
 * current host through the @fqref{managerApi.HostSession.host}
 * "HostSession.host" method
 *
 * @todo Add auditing functionality.
 */
class OPENASSETIO_CORE_EXPORT Host final {
 public:
  /**
   * Constructs a new Host wrapping the supplied host interface.
   */
  [[nodiscard]] static HostPtr make(hostApi::HostInterfacePtr hostInterface);

  /**
   * @name Host Information
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify the Host.
   *
   * The identifier will be different for each tool or application,
   * but common to all versions of any one. The identifier will use
   * only alpha-numeric characters and '.', '_' or '-', commonly in
   * the form of a 'reverse-DNS' style string, for example:
   *
   *     "org.openassetio.test.host"
   */
  [[nodiscard]] Identifier identifier() const;

  /**
   * Returns a human readable name to be used to reference this
   * specific host in user-facing messaging.
   * For example:
   *
   *     "OpenAssetIO Test Host"
   */
  [[nodiscard]] Str displayName() const;

  /**
   * Returns other information that may be useful about the host.
   * This can contain arbitrary key/value pairs. There should be no
   * reliance on a specific key being supplied by all hosts. The
   * information may be more generally useful for diagnostic or
   * debugging purposes. For example:
   *
   *     { 'version' : '1.1v3' }
   */
  [[nodiscard]] InfoDictionary info() const;

  /**
   * @}
   */

 private:
  explicit Host(hostApi::HostInterfacePtr hostInterface);
  hostApi::HostInterfacePtr hostInterface_;
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
