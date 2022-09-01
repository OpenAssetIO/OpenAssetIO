// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <memory>
#include <optional>
#include <string>

#include <openassetio/export.h>
#include <openassetio/BatchElementError.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(Context)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for a host application.

 If you are a asset management system developer, see @ref managerApi.
*/
namespace hostApi {

OPENASSETIO_DECLARE_PTR(Manager)

/**
 * The Manager is the Host facing representation of an @ref
 * asset_management_system. The Manager class shouldn't be directly
 * constructed by the host. An instance of the class for any given
 * asset management system can be retrieved from a
 * @fqref{hostApi.ManagerFactory} "ManagerFactory", using the
 * @fqref{hostApi.ManagerFactory.createManager}
 * "ManagerFactory.createManager()" method with an appropriate manager
 * @ref identifier.
 *
 * @code
 * factory = openassetio.hostApi.ManagerFactory(
 *     hostImpl, consoleLogger, pluginFactory)
 * manager = factory.createManager("org.openassetio.test.manager")
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
  /**
   * Constructs a new Manager wrapping the supplied manager interface
   * and host session.
   */
  static ManagerPtr make(managerApi::ManagerInterfacePtr managerInterface,
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
   * This identifier is used with the @fqref{hostApi.ManagerFactory}
   * "ManagerFactory" to select which Manager to initialize, and so can
   * be used in preferences etc to persist the chosen Manager. The
   * identifier will use only alpha-numeric characters and '.', '_' or
   * '-'. They generally follow the 'reverse-DNS' style, for example:
   *
   *     "org.openassetio.test.manager"
   */
  [[nodiscard]] Identifier identifier() const;

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
   * @{
   */

  /**
   * @todo Document settings mechanism
   *
   * @return Any settings relevant to the function of the manager with
   * their current values (or their defaults if @ref initialize has
   * not yet been called).
   *
   * Some managers may not have any settings, so this function will
   * return an empty dictionary.
   */
  [[nodiscard]] InfoDictionary settings() const;

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
  void initialize(InfoDictionary managerSettings);

  /**
   * @}
   */

  /**
   * @name Policy
   *
   * @{
   */
  /**
   * Determines if the manager is interested in participating in
   * interactions with entities with the specified sets of @ref trait
   * traits. The supplied @ref Context determines whether this is for
   * resolution or publishing. It is *vital* to call this before
   * attempting to publish data to the manager, as the entity
   * @ref trait_set you desire to work with may not be supported.
   *
   * For example, you would call this in order to see if the manager
   * would like to manage the path of a scene file whilst choosing a
   * destination to save to.
   *
   * This information should then be used to determine which options
   * should be presented to the user. For example, if the returned
   * @fqref{TraitsData} "TraitsData" is not imbued with the @ref
   * traits.managementPolicy.ManagedTrait "ManagedTrait" for a query as
   * to the management of scene files, you should hide or disable menu
   * items that relate to publish or loading of assetized scene files.
   *
   * If a returned @fqref{TraitsData} "TraitsData" is imbued with the
   * @ref traits.managementPolicy.ManagedTrait "ManagedTrait", then it
   * can be assumed that the manager is capable of retrieving (for a
   * read context) and storing (for a write context) all of the
   * supplied traits through @ref resolve and @ref register.
   *
   * @warning The @fqref{Context.access} "access" of the supplied
   * context will be considered by the manager. If it is set to read,
   * then it's response applies to resolution. If write, then it
   * applies to publishing. Ignored reads can allow optimisations in
   * a host as there is no longer a need to test/resolve applicable
   * strings.
   *
   * @note One very important trait that may be imbued in the
   * policy is the @ref openassetio.traits.managementPolicy.WillManagePathTrait
   * "WillManagePathTrait". If set, you can assume the asset
   * management system will manage the path to use for the creation
   * of any new assets. you must then always call @ref preflight
   * before any file creation to allow the asset management system to
   * determine and prepare the work path, and then use this path to
   * write data to, prior to calling @ref register. If this trait is
   * not imbued, then you should take care of writing data yourself
   * (maybe prompting the user for a location on disk), and then only
   * call @ref register to create the new entity.
   *
   * @param traitSets The entity @ref trait "traits" to query.
   *
   * @param context The calling context.
   *
   * @return a `TraitsData` for each element in `traitSets`.
   */
  [[nodiscard]] trait::TraitsDatas managementPolicy(const trait::TraitSets& traitSets,
                                                    const ContextConstPtr& context) const;

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
   *  contextFromPersistenceToken for future API use in another session
   *  with the same manager.
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
  Str persistenceTokenForContext(const ContextPtr& context);

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
  ContextPtr contextFromPersistenceToken(const Str& token);

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
   * @warning It is essential, as a host, that only valid references are
   * supplied to Manager API calls. Before any reference is passed to
   * any other methods of this class, they must first be validated
   * through this method.
   *
   * Determines if the supplied string (in its entirety) matches the
   * pattern of an @ref entity_reference.  It does not verify that it
   * points to a valid entity in the system, simply that the pattern of
   * the string is recognised by the manager.
   *
   * If it returns `true`, the string is an @ref entity_reference and
   * should be considered as a managed entity (or a future one).
   * Consequently, it should be resolved before use. It also confirms
   * that it can be passed to any other method that requires an @ref
   * entity_reference.
   *
   * If `false`, this manager should no longer be involved in actions
   * relating to the string.
   *
   * This function is useful for control flow where constructing an
   * @fqref{EntityReference} "EntityReference" object is not (yet)
   * needed. For other situations, consider using @ref
   * createEntityReferenceIfValid instead, to validate and (potentially)
   * return an `EntityReference` in a single call.
   *
   * @param someString `str` The string to be inspected.
   *
   * @return `bool` `True` if the supplied token should be
   * considered as an @ref entity_reference, `False` if the pattern
   * is not recognised.
   *
   * @note This call does not verify an entity exits, just that the
   * format of the string is recognised. The call is notionally trivial
   * and does not involve back-end system queries.
   *
   * @see @needsref entityExists
   * @see @ref resolve
   *
   * @todo Make use of
   * openassetio.constants.kField_EntityReferencesMatchPrefix if
   * supplied, especially when bridging between C/python.
   */
  [[nodiscard]] bool isEntityReferenceString(const Str& someString) const;

  /**
   * Create an @ref EntityReference object wrapping a given
   * @ref entity_reference string.
   *
   * First validates that the given entity reference string is
   * meaningful for this manager via @ref isEntityReferenceString,
   * throwing a `std::domain_error` if not.
   *
   * @param entityReferenceString Raw string representation of the
   * entity reference. Taken by value to enable move semantics, on the
   * assumption that an invalid entity reference is a rare case.
   *
   * @return Validated entity reference object.
   *
   * @throw std::domain_error If the given string is not recognized as
   * an entity reference by this manager.
   *
   * @todo Use a custom exception type rather than std::domain_error.
   */
  [[nodiscard]] EntityReference createEntityReference(Str entityReferenceString) const;

  /**
   * Create an @ref EntityReference object wrapping a given
   * @ref entity_reference string, if it is valid according to
   * @ref isEntityReferenceString.
   *
   * @see @ref createEntityReference
   *
   * @param entityReferenceString Raw string representation of the
   * entity reference. Taken by value to enable move semantics, on the
   * assumption that an invalid entity reference is a rare case.
   *
   * @return `std::optional` containing an `EntityReference` value if
   * valid, not containing a value otherwise.
   */
  [[nodiscard]] std::optional<EntityReference> createEntityReferenceIfValid(
      Str entityReferenceString) const;

  /**
   * @}
   */

  /**
   * @name Entity Resolution
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
  using ResolveSuccessCallback = std::function<void(std::size_t, const TraitsDataPtr&)>;

  /**
   * Provides a @fqref{TraitsData} "TraitsData"
   * populated with the available data for the requested set of
   * traits for each given @ref entity_reference.
   *
   * This call will block until all resolutions are complete and
   * callbacks have been called. Callbacks will be called on the
   * same thread that called `resolve`
   *
   * Any traits that aren't applicable to any particular entity
   * reference will not be set in the returned data. Consequently, a
   * trait being set in the result is confirmation that an entity has
   * that trait.
   *
   * There is however, no guarantee that a manager will have data
   * for all of a traits properties. It is the responsibility of the
   * caller to handle requested data being missing in a fashion
   * appropriate to its intended use.
   *
   * @note @fqref{EntityReference} "EntityReference" objects _must_ be
   * constructed using either
   * @fqref{hostApi.Manager.createEntityReference}
   * "createEntityReference" or
   * @fqref{hostApi.Manager.createEntityReferenceIfValid}
   * "createEntityReferenceIfValid". As a convenience, you may check if
   * a string is a valid entity reference for the manager using
   * @fqref{hostApi.Manager.isEntityReferenceString}
   * "isEntityReferenceString" first.
   *
   * The API defines that all file paths passed though the API that
   * represent file sequences should retain the frame token, and
   * use the 'format' syntax, compatible with sprintf (eg.  %04d").
   *
   * There may be errors during resolution. These can either be
   * exceptions thrown from `resolve`, or @fqref{BatchElementError}
   * "BatchElementError"s given to the `errorCallback`. Exceptions are
   * unexpected errors that fail the whole batch. `BatchElementError`s
   * are errors that are specific to a particular entity - other
   * entities may still resolve successfully. Using HTTP status codes as
   * an analogy, typically a server error (5xx) would correspond to an
   * exception whereas a client error (4xx) would correspond to a
   * `BatchElementError`.
   *
   * @param entityReferences Entity references to query.
   *
   * @param context The calling context.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param successCallback Callback that will be called for each
   * successful resolution of an entity reference. It will be
   * given the corresponding index of the entity reference in
   * `entityRefs` along with its `TraitsData`. The callback will be
   * called on the same thread that initiated the call to `resolve`.
   *
   * @param errorCallback Callback that will be called for each
   * failed resolution of an entity reference. It will be given the
   * corresponding index of the entity reference in `entityRefs`
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `resolve`.
   */
  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               const ContextConstPtr& context, const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback);
  /**
   * @}
   */

  /**
   * @name Publishing
   *
   * The publishing functions allow the host to create an @ref entity
   * within the @ref asset_management_system represented by the Manager.
   * The API is designed to accommodate the broad variety of roles that
   * different asset managers embody. Some are 'librarians' that simply
   * catalog the locations of existing media. Others take an active role
   * in both the temporary and long-term paths to items they manage.
   *
   * There are two key components to publishing within this API.
   *
   * *1 - The Entity Reference*
   *
   * As with the other entry points in this API, it is assumed that an
   * @ref entity_reference is known ahead of time. How this reference is
   * determined is beyond the scope of this layer of the API, and
   * functions exists in higher levels that combine browsing and
   * publishing etc... Here, we simply assert that there must be a
   * meaningful reference given the @fqref{TraitsData} "TraitsData" of
   * the entity that is being created or published.
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
   * "traits" and their properties. The resulting @ref trait_set defines
   * the "type" of the entity, and the trait property values hold the
   * data for each specific entity.
   *
   * This means that OpenAssetIO it not just limited to working with
   * file-based data. Traits allow ancillary information to be managed
   * (such as the colorspace for an image), as well as container-like
   * entities such as shots/sequences/etc..
   *
   * For more on the relationship between Entities, Specifications and
   * traits, please see @ref entities_traits_and_specifications "this"
   * page.
   *
   * The action of 'publishing' itself, is split into two parts, depending on
   * the nature of the item to be published.
   *
   *  @li **Preflight** When you are about to create some new
   *  media/asset.
   *  @li **Registration** When you wish to publish media
   *  that exists.
   *
   * For examples of how to correctly call these parts of the API, see
   * the @ref examples page.
   *
   * @note The term '@ref publish' is somewhat loaded. It generally
   * means something different depending on who you are talking to. See
   * the @ref publish "Glossary entry" for more on this, but to help
   * avoid confusion, this API provides the @needsref updateTerminology
   * call, in order to allow the Manager to standardize some of the
   * language and terminology used in your presentation of the asset
   * management system with other integrations of the system.
   *
   * *3 - Thumbnails*
   *
   * The API provides a mechanism for a manager to request a thumbnail
   * for an entity as it is being published, see: @ref thumbnails.
   *
   * @{
   */

  /**
   * Callback signature used for a successful preflight operation on a
   * particular entity.
   */
  using PreflightSuccessCallback = std::function<void(std::size_t, EntityReference)>;

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to each supplied @ref
   * entity_reference. The entity does not need to exist yet (see
   * @ref entity_reference) or it may be a parent entity that you are
   * about to create a child of or some other similar relationship
   * (it actually doesn't matter really, as this @ref
   * entity_reference will ultimately have been determined by
   * interaction with the Manager, and it will have returned you
   * something meaningful).
   *
   * It should be called before register() if you are about to
   * create media or write to files. If the file or data already
   * exists, then preflight is not needed. It will return a working
   * @ref entity_reference for each given entity, which can be
   * resolved in order to determine a working path that the files
   * should be written to.
   *
   * This call is designed to allow sanity checking, placeholder
   * creation or any other sundry preparatory actions to be carried
   * out by the Manager. In the case of file-based entities,
   * the Manager may even use this opportunity to switch to some
   * temporary working path or some such.
   *
   * @note It's vital that the @ref Context is well configured here,
   * in particular the @fqref{Context.retention}
   * "Context.retention".
   *
   * @warning The working @ref entity_reference returned by this
   * method should *always* be used in place of the original
   * reference supplied to `preflight` for resolves prior to
   * registration, and for the final call to @ref
   * register itself. See @ref example_publishing_a_file.
   *
   * @param entityReferences The entity references to preflight prior
   * to registration.
   *
   * @param traitSet The @ref trait_set of the
   * entites that are being published.
   *
   * @param context The calling context. This is not
   * replaced with an array in order to simplify implementation.
   * Otherwise, transactional handling has the potential to be
   * extremely complex if different contexts are allowed.
   *
   * @param successCallback Callback that will be called for each
   * successful preflight of an entity reference. It will be given
   * the corresponding index of the entity reference in
   * `targetEntityRefs` along with an updated reference to use for
   * future interactions as part of the publishing operation. The
   * callback will be called on the same thread that initiated the
   * call to `preflight`.
   *
   * @param errorCallback Callback that will be called for each
   * failed preflight of an entity reference. It will be given the
   * corresponding index of the entity reference in `entityRefs`
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `preflight`.
   *
   * @see @ref register
   */
  void preflight(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
                 const ContextConstPtr& context, const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback);

  /**
   * Callback signature used for a successful register operation on a
   * particular entity.
   */
  using RegisterSuccessCallback = std::function<void(std::size_t, EntityReference)>;

  /**
   * Register should be used to register new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * @note The registration call is applicable to all kinds of
   * Manager (path managing, or librarian), as long as the @ref
   * traits.managementPolicy.ManagedTrait "ManagedTrait" is present
   * in the response to @fqref{hostApi.Manager.managementPolicy}
   * "managementPolicy" for the traits of the entities you are
   * intending to register_. In this case, the Manager is saying it
   * doesn't handle entities with those traits, and it should not be
   * registered.
   *
   * As each @ref entity_reference has (ultimately) come from the
   * manager (either in response to delegation of UI/etc... or as a
   * return from another call), then it can be assumed that the
   * Manager will understand what it means for you to call `register`
   * on this reference with the supplied @fqref{TraitsData}
   * "TraitsData". The conceptual meaning of the call is:
   *
   * "I have this reference you gave me, and I would like to register
   * a new entity to it with the traits I told you about before. I
   * trust that this is ok, and you will give me back the reference
   * that represents the result of this."
   *
   * It is up to the manager to understand the correct result for the
   * particular trait set in relation to this reference. For example,
   * if you received this reference in response to browsing for a
   * target to `kWriteMultiple` and the traits of a
   * `ShotSpecification`s, then the Manager should have returned you
   * a reference that you can then register multiple
   * `ShotSpecification` entities to without error. Each resulting
   * entity reference should then reference the newly created Shot.
   *
   * @warning All supplied TraitsDatas should have the same trait
   * sets. If you wish to register different "types" of entity, they
   * need to be registered in separate calls.
   *
   * @warning When registering files, it should never be assumed
   * that the resulting @ref entity_reference will resolve to the
   * same path. Managers may freely relocate, copy, move or rename
   * files as part of registration.
   *
   * @param entityReferences Entity references to register_ to.
   *
   * @param entityTraitsDatas The data to register for each entity.
   * NOTE: All supplied instances should have the same trait set.
   *
   * @param context Context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful registration of an entity reference. It will be given
   * the corresponding index of the entity reference in
   * `targetEntityRefs` along with an updated reference to use for
   * future interactions with the resulting new entity. The callback
   * will be called on the same thread that initiated the call to
   * `register`.
   *
   * @param errorCallback Callback that will be called for each
   * failed registration of an entity reference. It will be given the
   * corresponding index of the entity reference in `entityRefs`
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `register`.
   *
   * @return None
   *
   * @exception `std::out_of_range` If `entityReferences` and
   * `entityTraitsDatas` are not lists of the same length.
   *
   * @exception `std::invalid_argument` If all `entityTraitsDatas` do
   * not share the same trait set.
   *
   * Other exceptions may be raised for fatal runtime errors, for
   * example server communication failure.
   *
   * @see @fqref{TraitsData} "TraitsData"
   * @see @ref preflight
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  void register_(const EntityReferences& entityReferences,
                 const trait::TraitsDatas& entityTraitsDatas, const ContextConstPtr& context,
                 const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback);

  /// @}

 private:
  explicit Manager(managerApi::ManagerInterfacePtr managerInterface,
                   managerApi::HostSessionPtr hostSession);

  managerApi::ManagerInterfacePtr managerInterface_;
  managerApi::HostSessionPtr hostSession_;
};
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
