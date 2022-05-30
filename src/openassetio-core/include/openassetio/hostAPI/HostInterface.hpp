// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostAPI {
/**
 * The HostInterface provides an abstraction of the 'caller of the
 * API'. Colloquially, we refer to this as the '@ref host'. This may be
 * a simple pipeline tool, or a full content creation application.
 *
 * The HostInterface provides a generic mechanism for a @ref manager to
 * query information about the identity of the host. In future, this
 * interface may be extended to include the ability to retrieve
 * information about available documents and their known entity
 * references.
 *
 * In order for a host to use the API, it must provide an
 * implementation of the HostInterface to the @ref
 * openassetio.hostAPI.Session class upon construction.
 *
 * A @ref manager does not call the HostInterface directly, it is
 * always accessed via the @ref openassetio.managerAPI.Host wrapper.
 * This allows the API to insert suitable house-keeping and auditing
 * functionality in between.
 */
class OPENASSETIO_CORE_EXPORT HostInterface {
 public:
  HostInterface() = default;

  /**
   * Polymorphic destructor.
   */
  virtual ~HostInterface() = default;

  /**
   * @name Host Information
   *
   * @{
   */

  /**
   * Returns an identifier that uniquely identifies the Host.
   *
   * This may be used by a Manager's @ref
   * openassetio.managerAPI.ManagerInterface "ManagerInterface" to
   * adjust its behavior accordingly. The identifier should be
   * unique for any application, but common to all versions.
   *
   * The identifier should use only alpha-numeric characters and '.',
   * '_' or '-'. We suggest using the "reverse DNS" style, for
   * example:
   *
   *    "org.openassetio.host.test"
   *
   * @return host identifier.
   */
  [[nodiscard]] virtual openassetio::Str identifier() const = 0;

  /**
   * Returns a human readable name to be used to reference this
   * specific host in user-facing presentations.
   *
   *     "OpenAssetIO Test Host"
   *
   * @return Host's display name.
   */
  [[nodiscard]] virtual Str displayName() const = 0;

  /**
   * Returns other information that may be useful about this Host.
   * This can contain arbitrary key/value pairs. Managers never rely
   * directly on any particular keys being set here, but the
   * information may be useful for diagnostic or debugging purposes.
   * For example:
   *
   * { 'version' : '1.1v3' }
   *
   * @return Arbitrary manager-specific info dictionary.
   *
   * @todo Definitions for well-known keys such as 'version' etc.
   */
  [[nodiscard]] virtual InfoDictionary info() const;
  /// @}
};

using HostInterfacePtr = SharedPtr<HostInterface>;
}  // namespace hostAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
