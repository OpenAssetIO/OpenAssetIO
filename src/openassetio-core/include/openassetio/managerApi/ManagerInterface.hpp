// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#pragma once

#include <memory>
#include <string>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerStateBase)
OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(Context)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for an asset management system.

 If you are a tool or application developer, see @ref hostApi.
*/
namespace managerApi {

OPENASSETIO_DECLARE_PTR(ManagerInterface)

/**
 * This Interface binds a @ref asset_management_system into
 * OpenAssetIO. It is not called directly by a @ref host, but by the
 * middleware that presents a more object-oriented model of this to
 * the @ref host - namely, the @ref openassetio.hostApi.Manager.
 *
 * It is structured around the following principles:
 *
 *   @li The currency of the API is either data, or an @ref
 *   entity_reference. objects should not be used to represent an @ref
 *   entity or its properties.
 *
 *   @li The manager plugin is expected to be batch-first. That is,
 *   where relevant, methods expect lists as their primary input
 *   parameters, and return a list as the result. This means a host
 *   can batch together multiple items and execute the same command
 *   on every item in the list in a single call, saving on
 *   potentially expensive round-trips and allowing the manager to
 *   use other back-end optimisations.
 *
 *   @li The interface is stateless as far as the host-facing API is
 *   concerned. The result of any method should solely depend on its
 *   inputs. This class could be static. In practice though, in a
 *   real-world session with a host, there are benefits to having an
 *   'instance' with a managed lifetime. This can be used to facilitate
 *   caching etc.
 *
 *   @li The implementation of this class should have no UI
 *   dependencies, so that it can be used in command-line only
 *   hosts/batch process etc...
 *
 *   @li You generally don't need to call the superclass implementation
 *   of any methods in this interface, unless you are deriving from your
 *   own subclass which requires it.
 *
 * Logging and Error Handling
 * --------------------------
 *
 * The supplied @fqref{managerApi.HostSession} "HostSession" object
 * provides access to a logger that allow messages and progress to be
 * reported back to the user. All logging should go through these
 * methods otherwise it may not be correctly presented to the user. The
 * loose term "user" also covers developers, who may need to see log
 * output for debugging and other purposes.
 *
 * @warning Your plugin may be hosted out of process, or even on
 * another machine, the HostSession bridge takes care of relaying
 * messages accordingly. Using custom logging mechanisms may well
 * result in output being lost.
 *
 * @see @fqref{managerApi.HostSession.logger} "HostSession.logger"
 * @see @fqref{log.LoggerInterface} "LoggerInterface"
 *
 * Exceptions should be thrown to handle any in-flight errors that
 * occur. The error should be mapped to a derived class of
 * exceptions.OpenAssetIOException, and thrown.  All exceptions of this
 * kind will be correctly passed across the plug-in C boundary,
 * and re-thrown. Other exceptions should not be used.
 *
 *  @see @ref openassetio.exceptions "exceptions"
 *
 * Threading
 * ---------
 * Any implementation of the ManagerInterface should be thread safe.
 * The one exception being @ref initialize, this will never be
 * called concurrently.
 *
 * When a @fqref{Context} "Context" object is constructed by
 * @fqref{hostApi.Manager.createContext} "createContext", the @ref
 * createState (or @ref createChildState for
 * @fqref{hostApi.Manager.createChildContext} "createChildContext")
 * method will be called, and the resulting state object stored in the
 * context. This context will then be re-used across related API calls
 * to your implementation of the ManagerInterface. You can use this to
 * determine which calls may be part of a specific 'action' in the same
 * host, or logically grouped processes such as a batch render. This
 * should allow you to implement stable resolution of @ref meta_version
 * "meta-versions" or other resolve-time concepts.
 *
 * There should be no persistent state in the implementation, concepts
 * such as getError(), etc.. for example should not be used.
 *
 * Hosts
 * -----
 *
 * Sometimes you may need to know more information about the API host.
 * A @ref openassetio.managerApi.Host object is available through the
 * @ref openassetio.managerApi.HostSession object passed to each method
 * of this class. This provides a standardised interface that all API
 * hosts guarantee to implement. This can be used to identify exactly
 * which host you are being called for, and query various entity
 * related specifics of the hosts data model.
 *
 * @see @ref openassetio.managerApi.Host "Host"
 *
 * Initialization
 * --------------
 *
 * The constructor makes a new instance, but at this point it is not
 * ready for use. Instances of this class should be light weight to
 * create, but don't have to be lightweight to initialize. The
 * informational methods must be available pre-initialization, so that
 * UI and other display-type queries can be made relatively cheaply to
 * provide users with a list of managers and their settings. None of
 * the entity-related methods will be called until after @ref
 * initialize has been called. The following methods must be callable
 * prior to initialization:
 *
 *    @li @ref identifier()
 *    @li @ref displayName()
 *    @li @ref info()
 *    @li @needsref updateTerminology()
 *    @li @ref settings()
 *
 * @todo Finish/Document settings mechanism.
 * @see @ref initialize
 */
class OPENASSETIO_CORE_EXPORT ManagerInterface {
 public:
  /**
   * Constructor.
   *
   * No work is done here - ManagerInterface instances should be cheap
   * to construct and stateless.
   */
  ManagerInterface();

  /**
   * Polymorphic destructor.
   */
  virtual ~ManagerInterface() = default;

  /**
   * @name Asset Management System Information
   *
   * These functions provide hosts with general information about the
   * @ref asset_management_system itself.
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify a specific asset
   * manager.
   *
   * This may be used by a host to persist the users preferred manager
   * via a preferences mechanism, or when spawning child processes,
   * etc...
   *
   * It should match the name used to register the plug-in with the
   * plug-in host.  The identifier should use only alpha-numeric
   * characters and '.', '_' or '-'.  Generally speaking, we recommend
   * using the 'reverse-DNS' convention, for example:
   *
   *     "org.openassetio.test.manager"
   *
   * @return Unique identifier of the manager.
   */
  [[nodiscard]] virtual Identifier identifier() const = 0;

  /**
   * Returns a human readable name to be used to reference this
   * specific asset manager in UIs or other user-facing messaging.
   *
   * One instance of its use may be in a host's preferences UI or
   * logging. For example:
   *
   *     "OpenAssetIO Test Asset Manager"
   *
   * @return Manager's display name.
   */
  [[nodiscard]] virtual Str displayName() const = 0;

  /**
   * Returns other information that may be useful about this @ref
   * asset_management_system. This can contain arbitrary key/value
   * pairs. For example:
   *
   *     { 'version' : '1.1v3', 'server' : 'assets.openassetio.org' }
   *
   * There are certain optional keys that may be used by a host or
   * the API:
   *
   *   @li openassetio.constants.kField_SmallIcon (upto 32x32)
   *   @li openassetio.constants.kField_Icon (any size)
   *
   * Because it can often be expensive to bridge between languages,
   * info can also contain an additional field - a prefix that
   * identifies a string as a valid entity reference. If supplied,
   * this will be used by the API to optimize calls to
   * isEntityReferenceString when bridging between C/Python etc.
   * If this isn't supplied, then isEntityReferenceString will always be
   * called to determine if a string is an @ref entity_reference or
   * not. Note, not all invocations require this optimization, so
   * @ref isEntityReferenceString should be implemented regardless.
   *
   *   @li openassetio.constants.kField_EntityReferencesMatchPrefix
   *
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] virtual InfoDictionary info() const;

  /**
   * @}
   */

  /**
   * @name Initialization
   *
   * @{
   */

  /**
   * @todo Document settings mechanism
   *
   * @param hostSession The API session.
   *
   * @return Any settings relevant to the function of the manager with
   * their current values (or their defaults if @ref initialize has
   * not yet been called).
   *
   * The default implementation returns an empty dictionary.
   */
  [[nodiscard]] virtual InfoDictionary settings(const HostSessionPtr& hostSession) const;

  /**
   * Prepares for interaction with a host.
   *
   * This is a good opportunity to initialize any persistent connections
   * to a back end implementation. It is fine for this call to block for
   * a period of time.
   *
   * If an exception is raised by this call, it signifies to the host
   * that a fatal error occurred, and this @ref
   * asset_management_system is not available with the current
   * settings.
   *
   * If no exception is raised, it can be assumed that the @ref
   * asset_management_system is ready. It is the implementations
   * responsibility to deal with transient connection errors (if
   * applicable) once initialized.
   *
   * The behavior of calling initialize() on an already initialized
   * instance should be a no-op, but if an error was raised
   * previously, then initialization should be re-attempted.
   *
   * @note This will always be called prior to any Entity-related
   * calls. An exception should be raised if this is not the case. It
   * is however, the following functions may be called prior to
   * initialization:
   *
   *  @li @ref identifier()
   *  @li @ref displayName()
   *  @li @ref info()
   *  @li @needsref updateTerminology()
   *  @li @ref settings()
   *
   * @todo We need a 'teardown' method to, before a manager is
   * de-activated in a host, to allow any event registrations etc...
   * to be removed.
   */
  virtual void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) = 0;

  /**
   * @}
   */

  /**
   * @name Policy
   *
   * @{
   */
  /**
   * Determines if the asset manager is interested in participating
   * in interactions with @ref entity "entities" with the specified
   * sets of @ref trait "traits".
   *
   * For example, a host may call this in order to see if the manager
   * would like to manage the path of a scene file whilst choosing a
   * destination to save to.
   *
   * This information is then used to determine which options should
   * be presented to the user or which workflows may be performed by
   * the host. For example, if @ref
   * traits.managementPolicy.ManagedTrait "ManagedTrait" was not
   * imbued for a query as to the management of scene files, a Host
   * will hide or disable menu items that relate to publish or
   * loading of assetized scene files, and not involve the manager in
   * any actions realting to scene files.
   *
   * @warning The @fqref{Context.access} "access"
   * specified in the supplied context should be carefully considered.
   * A host will independently query the policy for both read and
   * write access to determine if resolution and publishing features
   * are applicable to this implementation.
   *
   * @note One very important trait that may be imbued in the policy
   * is the @ref traits.managementPolicy.WillManagePathTrait
   * "WillManagePathTrait". If set, this instructs the host that the
   * asset management system will manage the path use for the
   * creation of any new assets. When set, @ref preflight will be
   * called before any file creation to allow the asset management
   * system to determine and prepare the work path. If this trait is
   * not imbued, then only @ref register will ever be called, and the
   * user will be tasked with determining where new files should be
   * located. In many cases, this greatly reduces the sophistication
   * of the integration as registering the asset becomes a partially
   * manual task, rather than one that can be fully automated for new
   * assets.
   *
   * For read contexts, the @ref traits.managementPolicy.ManagedTrait
   * "ManagedTrait" should only be imbued in the returned
   * @fqref{TraitsData} "TraitsData" if the manager can potentially
   * resolve data for all of the supplied traits. Hosts are required
   * to deal with the properties for any given trait being unset when
   * resolved, as they may not be available for existing assets, as
   * long as the traits are understood.
   *
   * For write contexts, the @ref traits.managementPolicy.ManagedTrait
   * "ManagedTrait" should only be imbued if the manager is capable
   * of persisting all traits (and any of their property data) when
   * they are registered for an entity, and returning that data via
   * resolve.
   *
   * @param traitSets The entity @ref trait "traits" to query.
   *
   * @param context The calling context.
   *
   * @param hostSession The API session.
   *
   * @return a `TraitsData` for each element in `traitSets`.
   */
  [[nodiscard]] virtual trait::TraitsDatas managementPolicy(
      const trait::TraitSets& traitSets, const ContextConstPtr& context,
      const HostSessionPtr& hostSession) const = 0;

  /**
   * @}
   */

  /**
   *
   * @name Manager State
   *
   * A single 'task' in a host, may require more than one interaction
   * with the asset management system.
   *
   * Because the @ref ManagerInterface is effectively state-less. To
   * simplify error handling, and allow an implementation to know which
   * interactions are related, this API supports the concept of a @ref
   * manager_state object. This is contained in every @ref Context and
   * passed to relevant calls.
   *
   * This mechanism may be used for a variety of purposes. For example,
   * it could ensure that queries are made from a coherent time stamp
   * during a render, or to undo the publishing of multiple assets.
   *
   * @{
   */

  /**
   *
   * Create a new object to represent the state of the interface and
   * return it (or some handle that can be persisted within the
   * context). You are free to implement this however you like, as
   * long as it can be uniquely represented by the object returned
   * from this function.
   *
   * This method is called whenever a new @ref Context is made by a
   * @fqref{hostApi.Manager.createContext} "createContext". The return
   * is then stored in the newly created Context, and is consequently
   * available to all the API calls in the ManagerInterface that take a
   * Context instance via @fqref{Context.managerState} "managerState".
   * Your implementation can then use this to anchor the api call to a
   * particular snapshot of the state of the asset inventory.
   *
   * The default implementation of this method returns a nullptr,
   * indicating that the manager does not perform custom state
   * management. Manager's implementing this method must also implement
   * @ref createChildState, @ref persistenceTokenForState and @ref
   * stateFromPersistenceToken.
   *
   * @param hostSession openassetio.managerApi.HostSession, The host
   * session that maps to the caller. This should be used for all
   * logging and provides access to the openassetio.managerApi.Host
   * object representing the process that initiated the API session.
   *
   * @return Some object that represents self-contained state of the
   * ManagerInterface. This will be passed to future calls.
   *
   * @exception exceptions.StateError If for some reason creation
   * fails.
   *
   * @see @ref createChildState
   * @see @ref persistenceTokenForState
   * @see @ref stateFromPersistenceToken
   */
  [[nodiscard]] virtual ManagerStateBasePtr createState(const HostSessionPtr& hostSession);

  /**
   * Create a state that is a child of the supplied state.
   *
   * This method is called whenever a child @ref Context is made by
   * @fqref{hostApi.Manager.createChildContext} "createChildContext".
   * The return is then stored in the newly created Context, and is
   * consequently available to all the API calls in the ManagerInterface
   * that take a Context instance via @fqref{Context.managerState}
   * "managerState". Your implementation can then use this to anchor the
   * api call to a particular snapshot of the state of the asset
   * inventory.
   *
   * The default implementation will raise if called. This method must
   * be implemented by any manager implementing @ref createState.
   *
   * @param hostSession openassetio.managerApi.HostSession, The host
   * session that maps to the caller. This should be used for all
   * logging and provides access to the openassetio.managerApi.Host
   * object representing the process that initiated the API session.
   *
   * @param parentState obj, The new state is to be considered a
   * 'child' of the supplied state. This may be used when creating a
   * child Context for persistence somewhere in a UI, etc... when
   * further processing may change the access/retention of the
   * Context. It is expected that the manager will migrate any
   * applicable state components to this child context, for example -
   * a timestamp used for 'vlatest'.
   *
   * @return Some object that represents self-contained state of the
   * ManagerInterface. This will be passed to future calls.
   *
   * @exception exceptions.StateError If for some reason creation
   * fails.
   * @exception std::runtime_error If called on a manager that does not
   * implement custom state management.
   *
   * @see @ref createState
   * @see @ref persistenceTokenForState
   * @see @ref stateFromPersistenceToken
   */
  [[nodiscard]] virtual ManagerStateBasePtr createChildState(
      const ManagerStateBasePtr& parentState, const HostSessionPtr& hostSession);

  /**
   * Returns a string that encapsulates the current state of the
   * ManagerInterface represented by the supplied state
   * object, (created by @ref createState or @ref createChildState)
   * so that can be restored later, or in another process.
   *
   * @return  A string that can be used to restore the stack.
   *
   * @exception std::runtime_error If called on a manager that does not
   * implement custom state management.
   *
   * @see @ref stateFromPersistenceToken
   */
  [[nodiscard]] virtual std::string persistenceTokenForState(const ManagerStateBasePtr& state,
                                                             const HostSessionPtr& hostSession);

  /**
   * Restores the supplied state object to a previously persisted
   * state.
   *
   * @return A state object, as per createState(), except restored to
   * the previous state encapsulated in the token, which is the same
   * string as returned by persistenceTokenForState.
   *
   * @exception exceptions.StateError If the supplied token is not
   * meaningful, or that a state has already been restored.
   * @exception std::runtime_error If called on a manager that does not
   * implement custom state management.
   */
  [[nodiscard]] virtual ManagerStateBasePtr stateFromPersistenceToken(
      const std::string& token, const HostSessionPtr& hostSession);
  /**
   * @}
   */

  /**
   * @name Entity Reference inspection
   *
   * Because of the nature of an @ref entity_reference, it is often
   * necessary to determine if some working string is actually an @ref
   * entity_reference or not, to ensure it is handled correctly.
   *
   * @{
   */

  /**
   * Determines if the supplied string (in its entirety) matches the
   * pattern of a valid @ref entity_reference in your system. It
   * does not need to verify that it points to a valid entity in the
   * system, simply that the pattern of the string is recognised by
   * this implementation.
   *
   * Return `True` if the string is an @ref entity_reference
   * and should be considered usable with the other methods of this
   * interface.
   *
   * Return `False`, if this should no longer be involved in actions
   * relating to the string as it is not recognised.
   *
   * @warning The result of this call should not depend on the context
   * Locale, and should be trivial to compute. If for example, a manager
   * makes use of URL-based entity references, then it is sufficient to
   * check that the string's schema is that owned by the manager. This
   * method should not validate the correctness of all supplied host,
   * path or query components. The API middleware may cache or
   * short-circuit calls to this method when bridging between languages.
   *
   * @param someString str The string to be inspected.
   *
   * @param hostSession HostSession The API session.
   *
   * @return `bool` `True` if the supplied string should be
   * considered as an @ref entity_reference, `False` if the pattern is
   * not recognised.
   *
   * @note This call should not verify an entity exits, just that the
   * format of the string is recognised as a potential entity reference
   * by the manager.
   *
   * @see @needsref entityExists
   * @see @needsref resolve
   */
  [[nodiscard]] virtual bool isEntityReferenceString(const std::string& someString,
                                                     const HostSessionPtr& hostSession) const = 0;

  /**
   * @}
   */
};
}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
