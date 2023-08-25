// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

OPENASSETIO_DECLARE_PTR(HostInterface)

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
 * In order for a host to use the API, it must provide an implementation
 * of the HostInterface to the @fqref{hostApi.ManagerFactory}
 * "ManagerFactory" class upon construction.
 *
 * A @ref manager does not call the HostInterface directly, it is
 * always accessed via the @ref openassetio.managerApi.Host wrapper.
 * This allows the API to insert suitable house-keeping and auditing
 * functionality in between.
 *
 * @note OpenAssetIO makes use of shared pointers to facilitate object
 * lifetime management across multiple languages. Instances passed into
 * API methods via shared pointer may have their lifetimes extended
 * beyond that of your code.
 */
class OPENASSETIO_CORE_EXPORT HostInterface {
 public:
  OPENASSETIO_ALIAS_PTR(HostInterface)

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
   * This may be used by a Manager's
   * @fqref{managerApi.ManagerInterface} "ManagerInterface"
   * to adjust its behavior accordingly. The identifier should be
   * unique for any application, but common to all versions.
   *
   * The identifier should use only alpha-numeric characters and '.',
   * '_' or '-'. We suggest using the "reverse DNS" style, for
   * example:
   *
   *    "org.openassetio.test.host"
   *    "io.aswf.openrv"
   *    "com.foundry.nuke"
   *
   * @return host identifier.
   *
   * @see https://en.wikipedia.org/wiki/Reverse_domain_name_notation
   */
  [[nodiscard]] virtual Identifier identifier() const = 0;

  /**
   * Returns a human readable name to be used to reference this
   * specific host in user-facing presentations, for example:
   *
   *     "OpenAssetIO Test Host"
   *     "OpenRV"
   *     "Nuke"
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
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
