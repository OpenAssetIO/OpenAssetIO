// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd

#pragma once

#include <functional>
#include <memory>
#include <string>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/BatchElementError.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, EntityReferencePagerInterface)
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
 *    @li @ref updateTerminology()
 *    @li @ref settings()
 *
 * @todo Finish/Document settings mechanism.
 * @see @ref initialize
 *
 * @note OpenAssetIO makes use of shared pointers to facilitate object
 * lifetime management across multiple languages. Instances passed into
 * API methods via shared pointer may have their lifetimes extended
 * beyond that of your code.
 */
class OPENASSETIO_CORE_EXPORT ManagerInterface {
 public:
  OPENASSETIO_ALIAS_PTR(ManagerInterface)

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
   *
   * @see https://en.wikipedia.org/wiki/Reverse_domain_name_notation
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
   *   @li @ref constants.kInfoKey_SmallIcon (upto 32x32)
   *   @li @ref constants.kInfoKey_Icon (any size)
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
   *   @li @ref constants.kInfoKey_EntityReferencesMatchPrefix
   *
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] virtual InfoDictionary info() const;

  /**
   * This call gives the manager a chance to customize certain strings
   * used in a host's UI/messages.
   *
   * See @ref openassetio.hostApi.terminology "terminology" for known
   * keys. The values in stringDict can be freely updated to match the
   * terminology of the asset management system you are representing.
   *
   * For example, you may way a host's "Publish Clip" menu item to read
   * "Release Clip", so you would set the @ref
   * openassetio.hostApi.terminology.kTerm_Publish value to "Release".
   *
   * @see @ref openassetio.hostApi.terminology.defaultTerminology
   * "terminology.defaultTerminology"
   *
   * @param terms Map of terms to be substituted by the manager.
   *
   * @param hostSession The host session that maps to the caller. This
   * should be used for all logging and provides access to the
   * openassetio.managerApi.Host object representing the process that
   * initiated the API session.
   *
   * @return Substituted map of terms.
   */
  [[nodiscard]] virtual StrMap updateTerminology(StrMap terms,
                                                 const HostSessionPtr& hostSession) const;

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
   *  @li @ref updateTerminology()
   *  @li @ref settings()
   *
   * @todo We need a 'teardown' method to, before a manager is
   * de-activated in a host, to allow any event registrations etc...
   * to be removed.
   */
  virtual void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) = 0;

  /**
   * Clears any internal caches.
   *
   * Only applicable if the implementation makes use of any caching,
   * otherwise it is a no-op. In caching interfaces, this will cause any
   * retained data to be discarded to ensure future queries are fresh.
   *
   * @param hostSession The API session.
   */
  virtual void flushCaches(const HostSessionPtr& hostSession);

  /**
   * @}
   */

  /**
   * @name Policy
   *
   * @{
   */
  /**
   * Management Policy queries determine if the manager is interested in
   * participating in interactions with @ref entity "entities" with a
   * specified @ref trait_set, and which traits it is capable of
   * resolving or persisting data for.
   *
   * This method is usually called early on by a host to determine
   * whether to enable OpenAssetIO related functionality when handling
   * specific kinds of data. The host will often adapt its subsequent
   * behaviour to minimise unsupported interactions with the manager. In
   * high call volume scenarios (such as CG rendering), this can
   * potentially save hundreds of thousands of redundant calls into the
   * API for unmanaged entity traits.
   *
   * As such, the implementation of this method and careful
   * consideration of the responses it returns is critical.
   *
   * @note It is not _required_ that a Host calls this method before
   * invoking other API methods, and so methods such as @ref resolve or
   * @ref register_ must be tolerant of being called with unsupported
   * traits (fear not, there is a simple and established failure mode
   * for this situation).
   *
   * This method must return a @fqref{TraitsData} "TraitsData" for each
   * requested @ref trait_set. The implementation of this method should
   * carefully consider the @fqref{Context.access} "access" set in the
   * supplied @ref Context, and imbue suitable traits in the result to
   * define:
   *
   *   - Whether and how that kind of entity is managed (traits with the
   *    `managementPolicy` usage metadata)
   *   - Which of the requested set of traits that have properties that
   *     can be resolved/persisted by your implementation.
   *
   * Entity management is an opt-in mechanism, and returning an empty
   * TraitsData states that you do not manage data with that specific
   * @ref trait_set, and hosts should avoid making redundant calls into
   * the API or presenting asset-centric elements of a workflow to the
   * user.
   *
   * @note Because traits are specific to any given application of the
   * API, please refer to the documentation for any relevant companion
   * project(s) that provide traits and specifications for your specific
   * scenario. For example, the
   * <a href="https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation"
   * target="_blank">OpenAssetIO-MediaCreation</a> project provides
   * traits for common data types used in computer graphics and media
   * production. Use the concrete Trait/Specification classes provided
   * by these projects to manipulate the result TraitsData instead of
   * directly setting traits and properties with string literals.
   *
   * @warning The @fqref{Context.access} "access"
   * specified in the supplied context should be carefully considered.
   * A host will independently query the policy for both read and
   * write access to determine if resolution and publishing features
   * are applicable to this implementation.
   *
   * @param traitSets The entity @ref trait "traits" to query.
   *
   * @param context The calling context.
   *
   * @param hostSession The API session.
   *
   * @return a `TraitsData` for each element in @p traitSets.
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
   * further processing may change the access of the
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
  [[nodiscard]] virtual Str persistenceTokenForState(const ManagerStateBasePtr& state,
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
      const Str& token, const HostSessionPtr& hostSession);
  /**
   * @}
   */

  /**
   * @name Batch element error handling
   *
   * @{
   */
  /**
   * Callback signature used for an unsuccessful operation on an
   * element in a batch.
   *
   * This should be called for errors that are specific to a particular
   * reference in a batch. Exceptions can be thrown to indicate a
   * whole-batch error.
   *
   * @see @fqref{BatchElementError.ErrorCode} "ErrorCode" for
   * appropriate error codes.
   */
  using BatchElementErrorCallback = std::function<void(std::size_t, BatchElementError)>;
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
   * pattern of a valid @ref entity_reference in your system.
   *
   * It does not need to verify that it points to a valid entity in the
   * system, simply that the pattern of the string is recognised by this
   * implementation.
   *
   * @note If possible, consider supplying a @ref
   * constants.kInfoKey_EntityReferencesMatchPrefix "prefix" in your
   * @ref info() dictionary, so that calls to this method can be
   * circumvented by performing a (fast) string prefix check instead.
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
   * @see @ref entityExists
   * @see @ref resolve
   */
  [[nodiscard]] virtual bool isEntityReferenceString(const Str& someString,
                                                     const HostSessionPtr& hostSession) const = 0;

  /**
   * Callback signature used for a successful entity existence query.
   */
  using ExistsSuccessCallback = std::function<void(std::size_t, bool)>;

  /**
   * Called to determine if each @ref entity_reference supplied
   * points to an entity that exists in the @ref
   * asset_management_system, and that they can be resolved into
   * a meaningful string or otherwise queried.
   *
   * By 'exist' we mean 'is ready to be read'. For example,
   * entityExists may be called before attempting to read from a
   * reference that is believed to point to an image sequence, so
   * that alternatives can be found.
   *
   * In the future, this may need to be extended to cover a more
   * complex definition of 'existence' (for example, known to the
   * system, but not yet finalized). For now however, it should be
   * assumed to simply mean, 'ready to be consumed', and if only a
   * placeholder or un-finalized asset is available, `False` should
   * be returned.
   *
   * The supplied context's locale may contain information pertinent
   * to disambiguating this subtle definition of 'exists' in some
   * cases too, as it better explains the use-case of the call.
   *
   * @param entityReferences Entity references to query.
   *
   * @param context The calling context.
   *
   * @param hostSession The host session that maps to the caller, this
   * should be used for all logging and provides access to the Host
   * object representing the process that initiated the API session.
   *
   * @param successCallback Callback that must be called for each
   * successful check of an entity reference. It should be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a boolean indicating the existence (as defined above) of
   * the entity. The callback must be called on the same thread that
   * initiated the call to `entityExists`.
   *
   * @param errorCallback Callback that must be called for each
   * failed check of an entity reference. It should be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback must be called on the same thread
   * that initiated the call to `entityExists`.
   */
  virtual void entityExists(const EntityReferences& entityReferences,
                            const ContextConstPtr& context, const HostSessionPtr& hostSession,
                            const ExistsSuccessCallback& successCallback,
                            const BatchElementErrorCallback& errorCallback) = 0;

  /**
   * @}
   */

  /**
   * @name Entity Reference Resolution
   *
   * The concept of resolution is turning an @ref entity_reference into
   * the data for one or more @ref trait "traits" that are meaningful to
   * the situation. It could be a color space, a directory, a script or
   * a frame range for an image sequence.
   *
   * @{
   */

  /**
   * Callback signature used for a successful entity resolution.
   */
  using ResolveSuccessCallback = std::function<void(std::size_t, TraitsDataPtr)>;

  /**
   * Provides the host with a @fqref{TraitsData} "TraitsData" populated
   * with the available data for the properties of the requested set of
   * traits for each given @ref entity_reference.
   *
   * This call should block until all resolutions are complete and
   * callbacks have been called. Callbacks must be called on the
   * same thread that called `resolve`.
   *
   * Requested traits that aren't applicable to any particular entity,
   * have no properties, or are not supported by your implementation,
   * should be ignored and not imbued to the result. Your
   * implementation of @ref managementPolicy when called with a read
   * @ref Context should accurately reflect which traits you understand
   * and are capable of resolving data for here.
   *
   * @warning See the documentation for each respective trait as to
   * which properties are considered required. It is the responsibility
   * of the caller to handle optional property values being missing in a
   * fashion appropriate to its intended use.
   *
   * @note Some trait properties may support substitution tokens, or
   * similar. The conventions for these will be defined in the trait's
   * documentation. See the originating project for more information on
   * their specifics. Don't forget to add a scheme and URL encode any
   * paths that are stored in properties defined as holding a URL.
   *
   * The Context should also be carefully considered to ensure that the
   * access does not violate any rules of the system - for example,
   * resolving an existing entity reference for write.
   *
   * The supplied entity references will have already been validated
   * as relevant to this manager (via
   * @fqref{hostApi.Manager.isEntityReferenceString}
   * "isEntityReferenceString").
   *
   * There may still be errors during resolution. An exception can be
   * thrown for unexpected errors that should fail the whole batch, and
   * it is up to the host to handle the exception. For errors specific
   * to a particular entity, where other entities may still resolve
   * successfully, an appropriate @fqref{BatchElementError}
   * "BatchElementError" should be given to the @p errorCallback. Using
   * HTTP status codes as an analogy, typically a server error (5xx)
   * would correspond to an exception whereas a client error (4xx) would
   * correspond to a `BatchElementError`.
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The traits to resolve for the supplied list of
   * entity references.
   *
   * @param context The calling context.
   *
   * @param hostSession The API session.
   *
   * @param successCallback Callback that must be called for each
   * successful resolution of an entity reference. It should be given
   * the corresponding index of the entity reference in
   * @p entityReferences along with its `TraitsData`. The callback must
   * be called on the same thread that initiated the call to `resolve`.
   *
   * @param errorCallback Callback that must be called for each
   * failed resolution of an entity reference. It should be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback must be called on the same thread
   * that initiated the call to `resolve`.
   *
   * @see @ref entityExists
   * @see @ref isEntityReferenceString
   * @see @fqref{BatchElementError} "BatchElementError"
   */
  virtual void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
                       const ContextConstPtr& context, const HostSessionPtr& hostSession,
                       const ResolveSuccessCallback& successCallback,
                       const BatchElementErrorCallback& errorCallback) = 0;
  /// @}

  /**
   * @name Related Entities
   *
   * A 'related' entity could take many forms. For example:
   *
   *  @li In 3D CGI, Multiple AOVs or layers may be related to a
   *  'beauty' render.
   *  @li In Compositing, an image sequence may be related to the script
   *  that created it.
   *  @li An asset may be related to a task that specifies work to be
   *  done.
   *  @li Parent/child relationships are also (semantically) covered by
   *  these relationships.
   *
   * In this API, these relationships are represented by trait data.
   * This may just compose property-less traits as a 'type', or
   * additionally, set trait property values to further define the
   * relationship. For example in the case of AOVs, the type might be
   * 'alternate output' and the attributes may be that the 'channel' is
   * 'diffuse'.
   *
   * Related references form a vital part in the abstraction of the
   * internal structure of the asset management system from the Host
   * application in its attempts to provide the user with meaningful
   * functionality. A good example of this is in an editorial example,
   * where it may need to query whether a 'shot' exists in a certain
   * part of the asset system. One approach would be to use a
   * 'getChildren' call, on this part of the system. This has the
   * drawback that is assumes that shots are always something that can
   * be described as 'immediate children' of the location in question.
   * This may not always be the case (say, for example there is some
   * kind of 'task' structure in place too). Instead we use a request
   * that asks for any 'shots' that relate to the chosen location. It is
   * then up to the implementation of the ManagerInterface to determine
   * how that maps to its own data model. Hopefully this allows Hosts of
   * this API to work with a broader range of asset managements, without
   * providing any requirements of their structure or data model.
   * @{
   */

  /**
   * Callback signature used for a successful entity relationship query.
   */
  using RelationshipSuccessCallback = std::function<void(std::size_t, EntityReferences)>;

  /**
   * Queries entity references that are related to the input
   * references by the relationship defined by a set of traits and
   * their properties in @p relationshipTraitsData.
   *
   * This is an essential function in this API - as it is widely used
   * to query other entities or organisational structure.
   *
   * @note Consult the documentation for the relevant relationship
   * traits to determine if the order of entities in the inner lists
   * of matching references is required to be meaningful.
   *
   * If any relationship definition is unknown, then an empty list
   * must be returned for that entity, and no errors raised. The
   * default implementation returns an empty list for all
   * relationships.
   *
   * @param entityReferences A list of @ref entity_reference
   * "entity references" to query the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have. May be empty.
   *
   * @param context The calling context.
   *
   * @param hostSession The host session that maps to the caller, this
   * should be used for all logging and provides access to the Host
   * object representing the process that initiated the API session.
   *
   * @param successCallback Callback that must be called for each
   * successful relationship query for an input entity reference. It
   * should be given the corresponding index of the entity reference
   * in @p entityReferences along with a list of entity references for
   * entities that have the relationship specified by
   * @p relationshipTraitsData. If there are no relations, an empty
   * list should be passed to the callback. The callback must be
   * called on the same thread that initiated the call to
   * `getWithRelationship`.
   *
   * @param errorCallback Callback that must be called for each
   * failed relationship query for an entity reference. It should be
   * given the corresponding index of the entity reference in
   * @p entityReferences along with a populated
   * @fqref{BatchElementError} "BatchElementError" (see
   * @fqref{BatchElementError.ErrorCode} "ErrorCodes"). The callback
   * must be called on the same thread that initiated the call to
   * `getWithRelationship`.
   *
   * @note Ensure that your implementation of @ref managementPolicy
   * responds appropriately when queried with relationship trait sets
   * and a read policy to communicate to the host whether or not you are
   * capable of handling queries for those relationships in this method.
   */
  virtual void getWithRelationship(const EntityReferences& entityReferences,
                                   const TraitsDataPtr& relationshipTraitsData,
                                   const trait::TraitSet& resultTraitSet,
                                   const ContextConstPtr& context,
                                   const HostSessionPtr& hostSession,
                                   const RelationshipSuccessCallback& successCallback,
                                   const BatchElementErrorCallback& errorCallback);

  /**
   * Queries entity references that are related to the input
   * reference by the relationships defined by a set of traits and
   * their properties. Each element of @p relationshipTraitsDatas
   * defines a specific relationship to query.
   *
   * This is an essential function in this API - as it is widely used
   * to query other entities or organisational structure.
   *
   * @note Consult the documentation for the relevant relationship
   * traits to determine if the order of entities in the inner lists
   * of matching references is required to be meaningful.
   *
   * If any relationship definition is unknown, then an empty list
   * must be returned for that relationship, and no errors raised. The
   * default implementation returns an empty list for all
   * relationships.
   *
   * @param entityReference The @ref entity_reference to query the
   * specified relationships for.
   *
   * @param relationshipTraitsDatas The traits of the relationships to
   * query.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have. May be empty.
   *
   * @param hostSession The host session that maps to the caller, this
   * should be used for all logging and provides access to the Host
   * object representing the process that initiated the API session.
   *
   * @param context Context The calling context.
   *
   * @param successCallback Callback that must be called for each
   * successful relationship query for an input relationship. It should
   * be given the corresponding index of the relationship definition in
   * @p relationshipTraitsDatas along with a list of entity references
   * for entities that are related to @p entityReference by that
   * relationship. If there are no relations, an empty list should be
   * passed to the callback. The callback must be called on the same
   * thread that initiated the call to `getWithRelationships`.
   *
   * @param errorCallback Callback that must be called for each failed
   * query for a relationship. It should be given the corresponding
   * index of the relationship in @p relationshipTraitsDatas along with
   * a populated BatchElementError (see BatchElementError.ErrorCode
   * "ErrorCodes"). The callback must be called on the same thread that
   * initiated the call to `getWithRelationships`.
   *
   * @note Ensure that your implementation of @ref managementPolicy
   * responds appropriately when queried with relationship trait sets
   * and a read policy to communicate to the host whether or not you are
   * capable of handling queries for those relationships in this method.
   */
  virtual void getWithRelationships(const EntityReference& entityReference,
                                    const trait::TraitsDatas& relationshipTraitsDatas,
                                    const trait::TraitSet& resultTraitSet,
                                    const ContextConstPtr& context,
                                    const HostSessionPtr& hostSession,
                                    const RelationshipSuccessCallback& successCallback,
                                    const BatchElementErrorCallback& errorCallback);

  /**
   * Callback signature used for a successful paged entity relationship
   * query.
   */
  using PagedRelationshipSuccessCallback =
      std::function<void(std::size_t, managerApi::EntityReferencePagerInterfacePtr)>;

  /**
   * Paged version of getWithRelationship. See non-paged
   * @ref getWithRelationship for further documentation.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param entityReferences A list of @ref entity_reference to query
   * the specified relationship for.
   *
   * @param pageSize The size of each page of data. The page size must
   * be fixed for the lifetime of pager object given to the @p
   * successCallback. Guaranteed to be greater than zero.
   *
   * @param context The calling context.
   *
   * @param hostSession The host session that maps to the caller, this
   * should be used for all logging and provides access to the Host
   * object representing the process that initiated the API session.
   *
   * @param successCallback Callback that should be called for each
   * successful relationship query. It should be given the corresponding
   * index of the entity reference in @p entityReferences as well as a
   * pager capable of returning pages of entities that have the
   * relationship to the entity at the corresponding index, specified by
   * @p relationshipTraitsData.
   *
   * The pager should be created by implementing @ref
   * EntityReferencePagerInterface, and should return results in pages
   * of size specified by @p pageSize
   *
   * If there are no relations, the pager should have no pages. The
   * callback should be called on the same thread that initiated the
   * call to `getWithRelationship`. To access the data, retrieve the
   * @fqref{hostApi.EntityReferencePager} from the callback, and use its
   * interface to traverse pages.
   *
   * @param errorCallback Callback that should be called for each failed
   * relationship query. It should be given the corresponding index of
   * the entity reference in @p entityReferences along with a populated
   * BatchElementError (see @ref BatchElementError.ErrorCode
   * "ErrorCodes"). The callback should be called on the same thread
   * that initiated the call to `getWithRelationship`.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   */
  virtual void getWithRelationshipPaged(const EntityReferences& entityReferences,
                                        const TraitsDataPtr& relationshipTraitsData,
                                        const trait::TraitSet& resultTraitSet, size_t pageSize,
                                        const ContextConstPtr& context,
                                        const HostSessionPtr& hostSession,
                                        const PagedRelationshipSuccessCallback& successCallback,
                                        const BatchElementErrorCallback& errorCallback);

  /**
   * Paged version of getWithRelationships. See non-paged
   * @ref getWithRelationships for further documentation.
   *
   * @param relationshipTraitsDatas The traits of the relationships to
   * query.
   *
   * @param entityReference The @ref entity_reference to query the
   * specified relationships for.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Guaranteed to be greater than zero.
   *
   * @param context The calling context.
   *
   * @param hostSession The host session that maps to the caller, this
   * should be used for all logging and provides access to the Host
   * object representing the process that initiated the API session.
   *
   * @param successCallback Callback that should be called for each
   * successful relationship query. It should be given the corresponding
   * index of the relationship in @p relationshipTraitsDatas as well as
   * a pager capable of returning pages of entities related to @p
   * entityReference by the relationship at that corresponding index.
   *
   * The pager should be created by implementing @ref
   * EntityReferencePagerInterface, and should return results in pages
   * of size specified by @p pageSize
   *
   * If there are no relations, the pager should have no pages. The
   * callback should be called on the same thread that initiated the
   * call to `getWithRelationship`. To access the data, retrieve the
   * @fqref{hostApi.EntityReferencePager} from the callback, and use its
   * interface to traverse pages.
   *
   * @param errorCallback Callback that should be called for each failed
   * relationship query. It should be given the corresponding index of
   * the relationship in @p relationshipTraitsDatas along with a
   * populated BatchElementError (see
   * @fqref{BatchElementError.ErrorCode} "ErrorCodes"). The callback
   * should be called on the same thread that initiated the call to
   * `getWithRelationships`.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @note The @ref trait_set of any queried relationship can be passed
   * to @ref managementPolicy in order to determine if the manager
   * handles relationships of that type.
   */
  virtual void getWithRelationshipsPaged(const EntityReference& entityReference,
                                         const trait::TraitsDatas& relationshipTraitsDatas,
                                         const trait::TraitSet& resultTraitSet, size_t pageSize,
                                         const ContextConstPtr& context,
                                         const HostSessionPtr& hostSession,
                                         const PagedRelationshipSuccessCallback& successCallback,
                                         const BatchElementErrorCallback& errorCallback);

  /// @}
  /**
   * @name Publishing
   *
   * The publishing functions allow a host create entities within the
   * @ref asset_management_system represented by this implementation.
   * The API is designed to accommodate the broad variety of roles that
   * different asset managers embody. Some are 'librarians' that simply
   * catalog the locations of existing media. Others take an active role
   * in both the temporary and long-term paths to items they manage.
   *
   * There are two key components to publishing within this API.
   *
   * **1 - The Entity Reference**
   *
   * As with the other entry points in this API, it is assumed that an
   * @ref entity_reference is known ahead of time. How this reference is
   * determined is beyond the scope of this layer of the API, and
   * functions exists in higher levels that combine browsing and
   * publishing etc... Here, we simply assert that there must be a
   * meaningful reference given the @ref trait_set of the entity that is
   * being created or published.
   *
   * @note 'Meaningful' is best defined by the asset manager itself. For
   * example, in a system that versions each 'asset' by creating
   * children of the asset for each version, when talking about where to
   * publish an image sequence of a render to, it may make sense to
   * reference to the Asset itself, so that the system can determine the
   * 'next' version number at the time of publish. It may also make
   * sense to reference a specific version of this asset to implicitly
   * state which version it will be written to. Other entity types may
   * not have this flexibility.
   *
   * **2 - TraitsData**
   *
   * The data for an entity is defined by one or more @ref trait
   * "Traits" and their properties. The resulting @ref trait_set
   * defines the "type" of the entity, and the trait property values
   * hold the data for each specific entity.
   *
   * This means that OpenAssetIO it not just limited to working with
   * file-based data. Traits allow ancillary information to be managed
   * (such as the colorspace for an image), as well as container-like
   * entities such as shots/sequences/etc.
   *
   * For more on the relationship between Entities, Specifications and
   * traits, please see @ref entities_traits_and_specifications
   * "this" page.
   *
   * The action of 'publishing' itself, is split into two parts,
   * depending on the nature of the item to be published.
   *
   *  @li **Preflight** When a Host is about to create some new
   *  media/asset.
   *  @li **Registration** When a Host is ready to publish
   *  media that exists.
   *
   * For examples of how to correctly call these parts of the
   * API within a host, see the @ref examples page.
   *
   * @note The term '@ref publish' is somewhat loaded. It generally
   * means something different depending on who you are talking to. See
   * the @ref publish "Glossary entry" for more on this, but to help
   * avoid confusion, this API provides the @ref updateTerminology
   * call, in order to allow the implementation to standardize some of
   * the language and terminology used in a Hosts presentation of the
   * asset management system with other integrations of the system.
   *
   * @{
   */

  /**
   * Callback signature used for a successful preflight operation on a
   * particular entity.
   */
  using PreflightSuccessCallback = std::function<void(std::size_t, EntityReference)>;

  /**
   * Prepares for some work to be done to create data for the
   * referenced entity. The entity may not yet exist (@ref
   * entity_reference). This call is designed to allow validation of
   * the target reference, placeholder creation or any other sundry
   * preparatory actions to be carried out.
   *
   * If this does not apply to the manager's workflow, then the
   * method can pass back the input reference once the target entity
   * reference has been validated.
   *
   * Generally, this will be called before register() when data is not
   * already immediately available for registration, to allow
   * placeholder actions to be performed. Note: depending on the
   * returned @fqref{managerApi.ManagerInterface.managementPolicy}
   * "managementPolicy", the host may make additional API queries using
   * the reference returned here before registration.
   *
   * This call must block until preflight is complete for all
   * supplied references, and callbacks have been called on the same
   * thread that called `preflight`
   *
   * @warning If the supplied @fqref{TraitsData} "trait data" is missing
   * required traits for any of the provided references (maybe they are
   * mismatched with the target entity), or the populated properties are
   * insufficient or invalid for upcoming @ref resolve for
   * @fqref{Context.Access.kWrite} "write" requests or the eventual
   * @ref register_, then error that element with an appropriate
   * @fqref{BatchElementError.ErrorCode}.
   *
   * @param entityReferences An @ref entity_reference for each entity
   * that it is desired to publish the forthcoming data to. See the
   * notes in the API documentation for the specifics of this.
   *
   * @param traitsHints @ref trait_set for each entity,
   * determining the type of entity to publish, complete with any
   * properties the host owns and can provide at this time. See @ref
   * glossary_preflight "glossary entry" for more information.
   *
   * @param context The calling context. This is not replaced with an
   * array in order to simplify implementation. Otherwise, transactional
   * handling has the potential to be extremely complex if different
   * contexts are allowed.
   *
   * @param hostSession The API session.
   *
   * @param successCallback Callback to be called for each successful
   * preflight of an entity reference. It should be called with the
   * corresponding index of the entity reference in @p entityReferences
   * along with the (potentially revised) working reference to be
   * used by the host for the rest of the publishing operation for
   * this specific entity (ie, resolve then register). This is an
   * opportunity to update the reference to one specific to any
   * placeholder/reserved entities if applicable. The callback must
   * be called on the same thread that initiated the call to
   * `preflight`.
   *
   * @param errorCallback Callback to be called for each failed
   * preflight of an entity reference. It should be called with the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback must be called on the same thread that
   * initiated the call to `preflight`. A
   * @fqref{BatchElementError.ErrorCode.kEntityAccessError}
   * "kEntityAccessError" should be used if the access pattern cannot be
   * adhered to, for example when attempting to write any target
   * references that are conceptually read-only in response to
   * @fqref{Context.Access.kWrite} "Access.kWrite", or in response to
   * @fqref{Context.Access.kCreateRelated} "Access.kCreateRelated" if
   * creating related entities is not supported. A
   * @fqref{BatchElementError.ErrorCode.kInvalidPreflightHint}
   * "kInvalidPreflightHint" should be used for any target references
   * who's corresponding @p traitsHints entry holds insufficient or
   * invalid information.
   *
   * @see @ref register_
   */
  virtual void preflight(const EntityReferences& entityReferences,
                         const trait::TraitsDatas& traitsHints, const ContextConstPtr& context,
                         const HostSessionPtr& hostSession,
                         const PreflightSuccessCallback& successCallback,
                         const BatchElementErrorCallback& errorCallback) = 0;

  /**
   * Callback signature used for a successful register operation on a
   * particular entity.
   */
  using RegisterSuccessCallback = std::function<void(std::size_t, EntityReference)>;

  /**
   * Publish entities to the @ref asset_management_system.
   *
   * This instructs the implementation to ensure a valid entity exists
   * for each given reference and to persist the data provided in the
   * @fqref{TraitsData}. This will be called either in isolation or
   * after calling preflight, depending on whether there is work needed
   * to be done to generate the data. Preflight is omitted if the data
   * is already available at the time of publishing.
   *
   * This call must block until registration is complete for all
   * supplied references, and callbacks have been called on the same
   * thread that called `register`
   *
   * This is an opportunity to do other things in the host as part of
   * publishing if required. The context's locale will tell you more
   * about the specifics of the calling application. Depending on the
   * implementation of your plugin, you can use this opportunity to
   * make use of the host-native SDK to extract additional
   * information or schedule additional processes to produce
   * derivative data.
   *
   * @warning It is a requirement of the API that the @ref trait_set of
   * the supplied TraitsData for each reference is persisted. This forms
   * the entity's 'type'. It is also a requirement that the properties
   * of any traits indicated as supported by your response to a
   * `managementPolicy` query for write context are persisted.
   *
   * If the supplied @ref trait_set is missing required traits for any
   * of the provided references (maybe they are mismatched with the
   * target entity, or missing essential data) then error that
   * element with an appropriate @fqref{BatchElementError.ErrorCode} "ErrorCode".
   *
   * @param entityReferences  The @ref entity_reference of each entity
   * to register_. It is up to the manager to ensure that this is
   * meaningful, as it is most likely implementation specific. For
   * example, if an entity with the traits of a 'Shot' specification is
   * requested to be published to a reference that points to a
   * 'Sequence' it makes sense to interpret this as a 'add a shot of
   * this spec to the sequence'. For other types of entity, there may be
   * different constraints on what makes sense.
   *
   * @param entityTraitsDatas The data for each entity (or 'asset') that
   * is being published. The implementation must persist the list of
   * traits, and any supported traits with properties. Such that a
   * subsequent call to @ref resolve for any of these traits contains
   * that data. It is guaranteed that the trait sets of these
   * instances are constant across the batch.
   *
   * @note Generally speaking, the data within the supplied
   * trait properties should be persisted verbatim. If however, the
   * implementation has any specific understanding of any given
   * trait, it is free to rewrite this data in any meaningful
   * fashion. The simplest example of this is the MediaCreation
   * `LocatableContent` trait, where the location URL may be updated to
   * the long-term persistent storage location of the registered data,
   * after it has been re-located by the manager.
   *
   * @param context The calling context. This is not
   * replaced with an array in order to simplify implementation.
   * Otherwise, transactional handling has the potential to be
   * extremely complex if different contexts are allowed.
   *
   * @param hostSession The API session.
   *
   * @param successCallback Callback to be called for each successful
   * registration. It should be called with the corresponding index
   * of the entity reference in @p entityReferences along with the
   * (potentially revised) final reference to be used by the host for
   * subsequent interactions with this specific entity. This is an
   * opportunity to update the reference to one specific to the
   * resulting entity and/or its specific version as applicable. The
   * callback must be called on the same thread that initiated the
   * call to `register`.
   *
   * @param errorCallback Callback to be called for each failed
   * registration. It should be called with the corresponding index
   * of the entity reference in @p entityReferences along with a
   * populated @fqref{BatchElementError} "BatchElementError" (see
   * @fqref{BatchElementError.ErrorCode} "ErrorCodes"). The callback
   * must be called on the same thread that initiated the call to
   * `register`.
   *
   * @see @fqref{TraitsData} "TraitsData"
   * @see @ref preflight
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  virtual void register_(const EntityReferences& entityReferences,
                         const trait::TraitsDatas& entityTraitsDatas,
                         const ContextConstPtr& context, const HostSessionPtr& hostSession,
                         const RegisterSuccessCallback& successCallback,
                         const BatchElementErrorCallback& errorCallback) = 0;

  /// @}
 protected:
  /**
   * Create an @ref EntityReference object wrapping a given @ref
   * entity_reference string. This should be used for all reference
   * creation by a manager's implementation.
   *
   * No validation is performed as this method is only visible to the
   * manager implementation, and so it is assumed that its internal
   * business logic inherently ensures only valid strings are
   * returned.
   *
   * @param entityReferenceString Raw string representation of the
   * entity reference.
   */
  [[nodiscard]] EntityReference createEntityReference(Str entityReferenceString) const;
};
}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
