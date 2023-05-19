// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

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
  OPENASSETIO_ALIAS_PTR(Manager)

  /**
   * Constructs a new Manager wrapping the supplied manager interface
   * and host session.
   */
  [[nodiscard]] static ManagerPtr make(managerApi::ManagerInterfacePtr managerInterface,
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
   * Management Policy queries allow a host to ask a Manager how they
   * would like to interact with different kinds of entity, and which
   * traits they are capable of resolving (or persisting). This allows
   * you to adapt application logic or user-facing behaviour
   * accordingly.
   *
   * Queries return a @fqref{TraitsData} "TraitsData" for each supplied
   * @ref trait_set, imbued with traits that describe the manager's
   * policy for entities with those traits, and which traits they are
   * capable of resolving/storing data for.
   *
   * This is an opt-in mechanism, such that if result is empty, then
   * the manager does not handle entities with the supplied traits.
   * In this situation, OpenAssetIO based functionality should be
   * disabled in the host when processing data of that type, and
   * traditional mechanisms used instead.
   *
   * This is particularly relevant for data types that may generate
   * large volumes of API requests, that can be avoided if the data in
   * question is not managed by the manager, or it can't resolve a
   * required trait.
   *
   * When querying this API, each Trait Set should be composed of:
   *
   *  - The trait set of the entity type in question. This is usually
   *    obtained from the relevant @ref Specification.
   *  - For read contexts, any additional traits with properties that
   *    you wish to resolve for that type of entity.
   *  - For write contexts, any additional traits with properties that
   *    you wish to publish for that type of entity.
   *
   * Along with the traits that describe the manager's desired
   * interaction pattern (ones with the `managementPolicy` usage
   * metadata), the resulting @fqref{TraitsData} "TraitsData" will be imbued with
   * (potentially a subset of) the requested traits, which the manager is
   * capable of resolving/persisting the properties for.
   *
   * If a requested trait is not present, then the manager will never
   * return properties for that trait in @ref resolve, or be able to
   * persist those properties with @ref register. This allows you to
   * know in advance if you can expect the configured manager to be able
   * to provide data you may require.
   *
   * @note Because traits are specific to any given application of the
   * API, please refer to the documentation for any relevant companion
   * project(s) that provide traits and specifications for your specific
   * scenario. For example, the
   * <a href="https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation"
   * target="_blank">OpenAssetIO-MediaCreation</a> project provides
   * traits for common data types used in computer graphics and media
   * production. Use the concrete Trait/Specification classes provided
   * by these projects to retrieve data from the supplied TraitsData
   * instead of querying directly using string literals.
   *
   * @warning The @fqref{Context.access} "access" of the supplied
   * context will be considered by the manager. If it is set to read,
   * then its response applies to resolution. If write, then it applies
   * to publishing. Managers may not handle both operations in the same
   * way. In most situations you will need to make separate queries for
   * read and write and adapt your business logic accordingly.
   *
   * @note There is no requirement to call this method before any other
   * API interaction, though it is strongly recommended to do so where
   * such information enables high-level behavioural changes or
   * optimisations that improve user experience.
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
   *  The @fqref{Context.locale} "locale" will be initialized with an
   *  empty @fqref{TraitsData} "TraitsData" instance.
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
   *  The new context will have the same configuration as the parent and
   *  be considered to be part of the same logical group, but may be
   *  modified independently. Useful when performing multiple operations
   *  in parallel.
   *
   *  @note The locale is deep-copied so that the child's locale can be
   *  freely modified without affecting the parent.
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
   * @name Batch element error handling
   *
   * @{
   */
  /**
   * Tag dispatching structure intended for use selecting appropriate
   * overloads for various error-handling modes.
   *
   * Many OpenAssetIO functions provide options as to whether errors are
   * handled via throwing exceptions, or by returning a variant based
   * result object.
   */
  struct BatchElementErrorPolicyTag {
    /**
     * Variant policy overloads, when used in a batch context, will be
     * exhaustive for all elements in the batch, a variant result
     * containing either a @ref TraitsData or @ref BatchElementError
     * will be provided for each @ref EntityReference provided as an
     * argument to the operation.
     */
    struct Variant {};
    /**
     * Exception policy overloads, when used in a batch context, will emit
     * an exception at the first encountered @ref BatchElementError
     * provided by the @ref ManagerInterface. This exception may not be in
     * index order.
     */
    struct Exception {};

    /**
     * Static instantiation of the @ref Variant dispatch tag, to avoid
     * the need to construct a new object to resolve dispatch methods.
     */
    static constexpr Variant kVariant{};
    /**
     * Static instantiation of the @ref Exception dispatch tag, to avoid
     * the need to construct a new object to resolve dispatch methods.
     */
    static constexpr Exception kException{};
  };

  /**
   * Callback signature used for an unsuccessful operation on an
   * element in a batch.
   *
   * This will be called for errors that are specific to a particular
   * reference in a batch. Exceptions can be thrown to indicate a
   * whole-batch error.
   *
   * The appropriate error code should be used for these errors. See
   * @fqref{BatchElementError.ErrorCode} "ErrorCode".
   */
  using BatchElementErrorCallback = std::function<void(std::size_t, BatchElementError)>;
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
  using ResolveSuccessCallback = std::function<void(std::size_t, TraitsDataPtr)>;

  /**
   * Provides a @fqref{TraitsData} "TraitsData" populated with the
   * available property data for the requested set of traits for each
   * given @ref entity_reference.
   *
   * This call will block until all resolutions are complete and
   * callbacks have been called. Callbacks will be called on the
   * same thread that called `resolve`
   *
   * @warning Only traits that are applicable to each entity, and for
   * which the manager has data, will be imbued in the result. See the
   * documentation for each respective trait to determine which
   * properties are considered required. It is the responsibility of the
   * caller to handle optional property values being missing in a
   * fashion appropriate to its intended use. The
   * @fqref{hostApi.Manager.managementPolicy} "managementPolicy" query
   * can be used ahead of time with a read @ref Context to determine
   * which specific traits any given manager supports resolving property
   * data for.
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
   *  Note that any properties that are defined as being a URL will be
   *  URL encoded. If it is expected that trait properties may contain
   *  substitution tokens or similar, their convention and behaviour
   *  will be defined in the documentation for the respective trait.
   *  Consult the originating project of the trait for more information.
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
   * This call will block until all resolutions are complete and
   * callbacks have been called. Callbacks will be called on the
   * same thread that called `resolve`
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
   * `entityReferences` along with its `TraitsData`. The callback will
   * be called on the same thread that initiated the call to `resolve`.
   *
   * @param errorCallback Callback that will be called for each
   * failed resolution of an entity reference. It will be given the
   * corresponding index of the entity reference in `entityReferences`
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `resolve`.
   */
  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               const ContextConstPtr& context, const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback);

  /**
   * Provides a @fqref{TraitsData} "TraitsData" populated with the
   * available data for the requested set of traits for the given @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Errors that occur during resolution will be thrown as an exception,
   * either from the @ref manager plugin (for errors not specific to the
   * entity reference) or as a @fqref{BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference Entity reference to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied entity
   * reference. Only traits applicable to the supplied entity reference
   * will be set in the resulting data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return Populated data.
   */
  TraitsDataPtr resolve(const EntityReference& entityReference, const trait::TraitSet& traitSet,
                        const ContextConstPtr& context,
                        const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @fqref{TraitsData} "TraitsData" or a
   * @fqref{BatchElementError} "BatchElementError".
   *
   * If successful, the result is populated with the
   * available data for the requested set of traits for the given @ref
   * entity_reference.
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to resolve this particular entity.
   *
   * Errors that are not specific to the entity being resolved will be
   * thrown as an exception.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReference Entity reference to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied entity
   * reference. Only traits applicable to the supplied entity reference
   * will be set in the resulting data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return Object containing either the populated data or an error
   * object.
   */
  std::variant<BatchElementError, TraitsDataPtr> resolve(
      const EntityReference& entityReference, const trait::TraitSet& traitSet,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Provides a @fqref{TraitsData} "TraitsData" populated with the
   * available data for the requested set of traits for each given @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Any errors that occur during resolution will be immediately thrown
   * as an exception, either from the @ref manager plugin (for errors
   * not specific to the entity reference) or as a
   * @fqref{BatchElementException} "BatchElementException"-derived
   * error.
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of populated data objects.
   */
  std::vector<TraitsDataPtr> resolve(
      const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
      const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @fqref{TraitsData} "TraitsData" or a
   * @fqref{BatchElementError} "BatchElementError" for each given @ref
   * entity_reference.
   *
   * For successful references, the corresponding element of the result
   * is populated with the available data for the requested set of
   * traits.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * resolve that particular entity.
   *
   * Errors that are not specific to an entity will be thrown as an
   * exception, failing the whole batch.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either the populated data
   * or an error.
   */
  std::vector<std::variant<BatchElementError, TraitsDataPtr>> resolve(
      const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

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
   * @warning If the supplied @ref trait_set is missing traits required
   * by the manager for any input entity reference, then that element
   * will error.
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
   * @param traitSet The @ref trait_set of the entities that are being
   * published.
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
   * corresponding index of the entity reference in `entityReferences`
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
   * This call signals your intent as a host application to do some
   * work to create data in relation to a supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on preflight behaviour.
   *
   * Any errors that occur during the preflight call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{BatchElementException} "BatchElementException"-derived
   * error.
   *
   * @param entityReference The entity reference to preflight prior
   * to registration.
   *
   * @param traitSet The @ref trait_set of the entity that is being
   * published.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions as part of
   * the publishing operation
   */
  EntityReference preflight(const EntityReference& entityReference,
                            const trait::TraitSet& traitSet, const ContextConstPtr& context,
                            const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to a supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on preflight behaviour.
   *
   * If successful, the result is populated with an updated reference
   * for use in future interactions in the publishing operation.
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to preflight this particular entity.
   *
   * Errors that are not specific to the entity will be thrown as an
   * exception.
   *
   * @param entityReference The entity reference to preflight prior
   * to registration.
   *
   * @param traitSet The @ref trait_set of the entity that is being
   * published.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Either an updated reference to use for future
   * interactions as part of the publishing operation, or an error
   * object detailing the reason for the failure of this particular
   * entity.
   */
  std::variant<BatchElementError, EntityReference> preflight(
      const EntityReference& entityReference, const trait::TraitSet& traitSet,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to each supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on preflight behaviour.
   *
   * Any errors that occur during the preflight call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to an entity reference) or as a
   * @fqref{BatchElementException} "BatchElementException"-derived
   * error.
   *
   * @param entityReferences The entity references to preflight prior
   * to registration.
   *
   * @param traitSet The @ref trait_set of the entities that are being
   * published.
   *
   * @param context The calling context. The same calling context is
   * used for each entity reference.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated references to use for future interactions as part
   * of the publishing operation
   */
  EntityReferences preflight(const EntityReferences& entityReferences,
                             const trait::TraitSet& traitSet, const ContextConstPtr& context,
                             const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to each supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitSet&, const ContextConstPtr&, <!--
   * --> const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on preflight behaviour.
   *
   * For successful references, the corresponding element of the result
   * is populated with an updated reference for use in future
   * interactions in the publishing operation.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * preflight that particular entity.
   *
   * Errors that are not specific to an entity will be thrown as an
   * exception.
   *
   * @param entityReferences The entity references to preflight prior
   * to registration.
   *
   * @param traitSet The @ref trait_set of the entity that is being
   * published.
   *
   * @param context The calling context. The same calling context is
   * used for each entity reference.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return A list where each element is either an updated reference to
   * use for future interactions as part of the publishing operation, or
   * an error object detailing the reason for the failure of that
   * particular entity.
   */
  std::vector<std::variant<BatchElementError, EntityReference>> preflight(
      const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Callback signature used for a successful register operation on a
   * particular entity.
   */
  using RegisterSuccessCallback = std::function<void(std::size_t, EntityReference)>;

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * @note The registration call is applicable to all kinds of Manager
   * (path managing, or librarian), as long as it includes a suitable
   * trait in the response to @fqref{hostApi.Manager.managementPolicy}
   * "managementPolicy" for the traits of the entities you are intending
   * to register. Otherwise, the Manager is saying it doesn't handle
   * entities with those traits, and it should not be registered.
   *
   * @warning The list of supported traits a manager returns in its @ref
   * managementPolicy response may be a subset of the trait set you
   * requested. This means that when data is registered, only property
   * values for those specific traits will be persisted, the rest will
   * be ignored. The full @ref trait_set will always be stored though,
   * to facilitate future identification.
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
   * @note All supplied TraitsDatas should have the same trait
   * sets. If you wish to register different "types" of entity, they
   * need to be registered in separate calls.
   *
   * @warning When registering traits that contain URLs or file paths
   * (for example the MediaCreation LocatableContent trait), it should
   * never be assumed that the resulting @ref entity_reference will
   * resolve to the same path. Managers may freely relocate, copy, move
   * or rename data as part of registration. Data for other trait
   * properties may also change if the entity has been otherwise
   * modified by some other interaction with the manager.
   *
   * @param entityReferences Entity references to register to.
   *
   * @param entityTraitsDatas The data to register for each entity.
   * NOTE: All supplied instances should have the same trait set,
   * batching with varying traits is not supported.
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
   * corresponding index of the entity reference in `entityReferences`
   * along with a populated @fqref{BatchElementError}
   * "BatchElementError" (see @fqref{BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `register`.
   *
   * @return None
   *
   * @exception std::out_of_range If `entityReferences` and
   * `entityTraitsDatas` are not lists of the same length.
   *
   * @exception std::invalid_argument If all `entityTraitsDatas` do
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

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, const ContextConstPtr&, <!--
   * --> const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * Any errors that occur during the register_ call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{BatchElementException} "BatchElementException"-derived
   * error.
   *
   * @param entityReference Entity reference to register to.
   *
   * @param entityTraitsData The data to register for the entity.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions with the
   * resulting new entity.
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  EntityReference register_(const EntityReference& entityReference,
                            const TraitsDataPtr& entityTraitsData, const ContextConstPtr& context,
                            const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, const ContextConstPtr&, <!--
   * --> const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * If successful, the result is populated with an updated reference
   * for use in future interactions with the resulting new entity
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to register this particular entity.
   *
   * Errors that are not specific to the entity will be thrown as an
   * exception.
   *
   * @param entityReference Entity reference to register to.
   *
   * @param entityTraitsData The data to register for the entity.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions with the
   * resulting new entity or an error object detailing the reason for
   * the failure of this particular entity.
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::variant<BatchElementError, EntityReference> register_(
      const EntityReference& entityReference, const TraitsDataPtr& entityTraitsData,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, const ContextConstPtr&, <!--
   * --> const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * Any errors that occur during the register_ call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{BatchElementException} "BatchElementException"-derived
   * error.
   *
   * @param entityReferences Entity references to register to.
   *
   * @param entityTraitsDatas The data to register for each entity.
   * NOTE: All supplied instances should have the same trait set,
   * batching with varying traits is not supported.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated references to use for future interactions with the
   * resulting new entities.
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::vector<EntityReference> register_(
      const EntityReferences& entityReferences, const trait::TraitsDatas& entityTraitsDatas,
      const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, const ContextConstPtr&, <!--
   * --> const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * For successful references, the corresponding element of the result
   * is populated with an updated reference for use in future
   * interactions with the resulting new entity.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * register that particular entity.
   *
   * Errors that are not specific to the entity will be thrown as an
   * exception.
   *
   * @param entityReferences Entity references to register to.
   *
   * @param entityTraitsDatas The data to register for each entity.
   * NOTE: All supplied instances should have the same trait set,
   * batching with varying traits is not supported.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return A list where each element is either an updated reference to
   * use in future interactions with the resulting new entity, or
   * an error object detailing the reason for the failure of that
   * particular entity.
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::vector<std::variant<BatchElementError, EntityReference>> register_(
      const EntityReferences& entityReferences, const trait::TraitsDatas& entityTraitsDatas,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /// @}

  /**
   * @private
   * Nothing to see here, this is working around an entertaining
   * situation in our Python -> C++ migration, whereby can't
   * expose the full Python Manager API if we make it in C++.
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  [[nodiscard]] managerApi::ManagerInterfacePtr _interface() const;
  // NOLINTNEXTLINE(readability-identifier-naming)
  [[nodiscard]] managerApi::HostSessionPtr _hostSession() const;

 private:
  explicit Manager(managerApi::ManagerInterfacePtr managerInterface,
                   managerApi::HostSessionPtr hostSession);

  managerApi::ManagerInterfacePtr managerInterface_;
  managerApi::HostSessionPtr hostSession_;
};
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
