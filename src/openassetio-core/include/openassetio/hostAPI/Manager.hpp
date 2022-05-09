// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for a host application.

 If you are a asset management system developer, see @ref managerAPI.
*/
namespace hostAPI {
/**
 * The Manager is the Host facing representation of an @ref
 * asset_management_system. The Manager class shouldn't be directly
 * constructed by the host.  An instance of the class for any given
 * asset management system can be retrieved from an API @needsref
 * Session, using the @ref
 * openassetio.hostAPI.Session.Session.currentManager
 * "Session.currentManager" method, after configuring the session with
 * the appropriate manager @ref identifier.
 *
 * @code
 * session = openassetio.hostAPI.Session(
 *     hostImpl, consoleLogger, pluginFactory)
 * session.useManager("org.openassetio.test")
 * manager = session.currentManager()
 * @endcode
 *
 * A Manager instance is the single point of interaction with an asset
 * management system. It provides methods to uniquely identify the
 * underlying implementation, querying and resolving @ref
 * entity_reference "entity references" and publishing new data.
 *
 * The Manager API is threadsafe and can be called from multiple
 * threads concurrently.
 */
class OPENASSETIO_CORE_EXPORT Manager {
 public:
  explicit Manager(managerAPI::ManagerInterfacePtr managerInterface);

  /**
   * @name Asset Management System Information
   *
   * These functions provide general information about the @ref
   * asset_management_system itself. These can all be called before
   * @needsref initialize has been called.
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify the Manager.
   *
   * This identifier is used with the Session class to select which
   * Manager to initialize, and so can be used as in preferences etc...
   * to persist the chosen Manager. The identifier will use only
   * alpha-numeric characters and '.', '_' or '-'. They generally follow
   * the 'reverse-DNS' style, for example:
   *
   *     "org.openassetio.manager.test"
   */
  [[nodiscard]] Str identifier() const;

  /**
   * Returns a human readable name to be used to reference this
   * specific asset manager in user-facing displays.
   * For example:
   *
   *     "OpenAssetIO Test Manager"
   */
  [[nodiscard]] Str displayName() const;

  /**
   * Returns other information that may be useful about this @ref
   * asset_management_system.  This can contain arbitrary key/value
   * pairs.For example:
   *
   *     { 'version' : '1.1v3', 'server' : 'assets.openassetio.org' }
   *
   * There is no requirement to use any of the information in the
   * info dict, but it may be useful for optimisations or display
   * customisation.
   *
   * There are certain well-known keys that may be set by the
   * Manager. They include things such as
   * openassetio.constants.kField_EntityReferencesMatchPrefix.
   */
  [[nodiscard]] InfoDictionary info() const;

  /**
   * @}
   */

 private:
  managerAPI::ManagerInterfacePtr managerInterface_;
};

}  // namespace hostAPI
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
