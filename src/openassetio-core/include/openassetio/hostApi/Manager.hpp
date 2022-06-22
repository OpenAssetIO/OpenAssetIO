// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <string>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for a host application.

 If you are a asset management system developer, see @ref managerApi.
*/
namespace hostApi {
/**
 * The Manager is the Host facing representation of an @ref
 * asset_management_system. The Manager class shouldn't be directly
 * constructed by the host.  An instance of the class for any given
 * asset management system can be retrieved from an API @needsref
 * Session, using the @ref
 * openassetio.hostApi.Session.Session.currentManager
 * "Session.currentManager" method, after configuring the session with
 * the appropriate manager @ref identifier.
 *
 * @code
 * session = openassetio.hostApi.Session(
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
  explicit Manager(managerApi::ManagerInterfacePtr managerInterface,
                   managerApi::HostSessionPtr hostSession);

  /**
   * @name Asset Management System Information
   *
   * These functions provide general information about the @ref
   * asset_management_system itself. These can all be called before
   * @ref initialize has been called.
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

  /**
   * @name Initialization
   *
   * @note Manager initialization is generally managed by the
   * @ref openassetio.hostApi.Session "Session" and these methods
   * generally don't need to be called directly by host code.
   *
   * @{
   */

  /**
   * Prepares the Manager for interaction with a host. In order to
   * provide light weight inspection of available Managers, initial
   * construction must be cheap. However most system require some
   * kind of handshake or back-end setup in order to make
   * entity-related queries. As such, the @ref initialize method is
   * the instruction to the Manager to prepare itself for full
   * interaction.
   *
   * If an exception is raised by this call, its is safe to assume
   * that a fatal error occurred, and this @ref
   * asset_management_system is not available, and should be retried
   * later.
   *
   * If no exception is raised, it can be assumed that the @ref
   * asset_management_system is ready. It is the implementations
   * responsibility to deal with transient connection errors (if
   * applicable) once initialized.
   *
   * The behavior of calling initialize() on an already initialized
   * Manager should be a no-op, but if an error was raised
   * previously, then initialization will be re-attempted.
   *
   * @note This must be called prior to any entity-related calls or
   * an Exception will be raised.
   *
   * @note This method may block for extended periods of time.
   *
   * @protected
   */
  void initialize();

  /**
   * @}
   */

  /**
   * @name Context Management
   * @see @ref stable_resolution
   *
   * @{
   */

  /**
   *  Creates a new Context for use with the manager.
   *
   *  @warning Contexts should never be directly constructed, always
   *  use this method or @ref createChildContext to create a new one.
   *
   *  @see @ref createChildContext
   *  @see @fqref{Context} "Context"
   */
  ContextPtr createContext();

  /**
   *
   *  Creates a child Context for use with the manager.
   *
   *  @warning Contexts should never be directly constructed, always
   *  use this method or @ref createContext to create a new one.
   *
   *  @param parentContext The new context will clone the supplied
   *  Context, and the Manager will be given a chance to migrate any
   *  meaningful state etc... This can be useful when certain UI
   *  elements need to 'take a copy' of a context in its current state
   *  in order to parallelise actions that are part of the same logical
   *  group, but have different locales, access or retention.
   *
   *  @see @ref createContext
   *  @see @fqref{Context} "Context"
   */
  ContextPtr createChildContext(const ContextPtr& parentContext);

  /**
   *  Returns a serializable token that represents the supplied
   *  context's managerState, such that it can be persisted or
   *  distributed between processes to associate subsequent API usage
   *  with the supplied context.
   *
   *  The returned token can be passed to @ref
   *  contextFromPersistenceToken for future API use in another @ref
   *  session with the same manager.
   *
   *  @param context The context to derive a persistence token for.
   *
   *  @return A persistence token that can be used with @ref
   *  contextFromPersistenceToken to create a context associated with
   *  the same logical group of actions as the one supplied to this
   *  method.
   *
   *  @warning This only encapsulates the logical identity of the
   *  Context, such that when restored, any API calls made using the
   *  resulting Context will be logically associated with the one
   *  supplied here. It does not encode the current access, retention
   *  or locale.
   *
   *  @see @ref stable_resolution
   */
  std::string persistenceTokenForContext(const ContextPtr& context);

  /**
   * Returns a @ref Context linked to a previous manager state, based
   * on the supplied persistence token derived from @ref
   * persistenceTokenForContext. This context, when used with API
   * methods will be considered part of the same logical series of
   * actions.
   *
   * @param token A token previously returned from @ref
   * persistenceTokenForContext by this manager.
   *
   * @return A context that will be associated with the same logical
   * group of actions as the context supplied to @ref
   * persistenceTokenForContext to generate the token.
   *
   * @warning The context's access, retention or locale is not
   * restored by this action.
   *
   * @see @ref stable_resolution
   *
   * @todo Should we concatenate the manager id in
   * persistenceTokenForContext so we can verify that they match?
   */
  ContextPtr contextFromPersistenceToken(const std::string& token);

  /**
   * @}
   */
 private:
  managerApi::ManagerInterfacePtr managerInterface_;
  managerApi::HostSessionPtr hostSession_;
};

using ManagerPtr = std::shared_ptr<Manager>;
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
