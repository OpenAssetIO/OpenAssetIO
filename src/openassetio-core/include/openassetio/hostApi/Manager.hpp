// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <type_traits>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/access.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/internal.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
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
class OPENASSETIO_CORE_EXPORT Manager final {
 public:
  OPENASSETIO_ALIAS_PTR(Manager)

  /**
   * Constructs a new Manager wrapping the supplied manager interface
   * and host session.
   */
  [[nodiscard]] static ManagerPtr make(managerApi::ManagerInterfacePtr managerInterface,
                                       managerApi::HostSessionPtr hostSession);

  /**
   * @name Asset Management System Identification
   *
   * These functions provide general identity information about the @ref
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
   * @}
   */

  /**
   * @name Asset Management System Information
   *
   * These functions provide general information about the @ref
   * asset_management_system itself.
   * @{
   */

  /**
   * Capabilities that the manager implements.
   *
   * Many OpenAssetIO methods are optional. This enum is used with the
   * introspection mechanism @ref hasCapability to provide a means of
   * querying which sets of methods the manager provides.
   */
  enum class Capability : std::underlying_type_t<internal::capability::manager::Capability> {
    /**
     * Manager makes use of the context to persist custom state for
     * performance reasons or otherwise.
     *
     * @note If this capability is true, then the host must reuse the
     * same context across related API calls (including the use of @ref
     * persistenceTokenForContext when the calls are distributed
     * cross-process).
     *
     * @see @ref stable_resolution
     */
    kStatefulContexts = internal::capability::manager::Capability::kStatefulContexts,
    /**
     * Manager customizes certain human-readable strings that the host
     * might want to use in UI/messages.
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref updateTerminology
     */
    kCustomTerminology = internal::capability::manager::Capability::kCustomTerminology,
    /**
     * Manager is capable of resolving @ref entity_reference into the
     * data for one or more @ref trait "traits".
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref resolve
     */
    kResolution = internal::capability::manager::Capability::kResolution,
    /**
     * Manager allows the host to create or update an @ref entity within
     * the @ref asset_management_system.
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref preflight
     * - @ref register_
     */
    kPublishing = internal::capability::manager::Capability::kPublishing,
    /**
     * Manager is capable of querying entity references that are related
     * to the input references by the relationship defined by a set of
     * traits and their properties.
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref getWithRelationship
     * - @ref getWithRelationships
     */
    kRelationshipQueries = internal::capability::manager::Capability::kRelationshipQueries,
    /**
     * Manager is capable of confirming the existence of entities.
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref entityExists
     */
    kExistenceQueries = internal::capability::manager::Capability::kExistenceQueries,

    /**
     * Manager may be capable of a providing an @ref EntityReference
     * considered to be a sensible default for a particular @ref
     * trait_set "trait set".
     *
     * This capability means the manager implements the following
     * methods:
     * - @ref defaultEntityReference
     */
    kDefaultEntityReferences = internal::capability::manager::Capability::kDefaultEntityReferences
  };

  /**
   * Query the manager as to which capabilities it implements.
   *
   * API methods are grouped into "capabilities", which are independent
   * groupings of functionality. For example, @ref
   * Capability.kPublishing "publishing" or @ref Capability.kResolution
   * "resolution".
   *
   * Support for each of these capabilities is optional for the manger,
   * and the default implementation will throw a
   * @fqref{errors.NotImplementedException} "NotImplementedException".
   *
   * This method can be called after @ref initialize to determine
   * whether a manager supports a given capability. It's a low-overhead
   * call, whose return value remains constant once the manager has been
   * initialized.
   *
   * For information on what methods belong to which capability set,
   * @see @ref Capability.
   *
   * @param capability The capability to check.
   *
   * @return Whether the manager has the capability in question.
   */
  [[nodiscard]] bool hasCapability(Capability capability);

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
   * openassetio.constants.kInfoKey_EntityReferencesMatchPrefix.
   */
  [[nodiscard]] InfoDictionary info();

  /**
   * This call gives the Manager a chance to customize certain strings
   * that you might want to use in your UI/messages.
   *
   * See @ref openassetio.hostApi.terminology "terminology" for
   * well-known keys. These keys are updated in the returned map to the
   * most appropriate term for the Manager. You should then use these
   * substitutions in any user-facing messages or display text so that
   * they feel at home.
   *
   * It's rare that you need to call this method directly, the @ref
   * openassetio.hostApi.terminology API provides more utility for far
   * less effort.
   *
   * @see @ref openassetio.hostApi.terminology "terminology"
   * @see @ref openassetio.hostApi.terminology.Mapper.replaceTerms
   * "Mapper.replaceTerms"
   * @see @ref openassetio.hostApi.terminology.defaultTerminology
   * "terminology.defaultTerminology"
   *
   * @param terms Map of terms to be substituted by the manager.
   *
   * @return Substituted map of terms.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kCustomTerminology.
   *
   * @see @ref Capability.kCustomTerminology
   */
  StrMap updateTerminology(StrMap terms);

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
  [[nodiscard]] InfoDictionary settings();

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
   * Manager is to re-initialize the manager with any updated settings
   * that are provided. If an error was raised previously, then
   * initialization will be re-attempted.
   *
   * @note This must be called prior to any entity-related calls or
   * an Exception will be raised.
   *
   * @note This method may block for extended periods of time.
   */
  void initialize(InfoDictionary managerSettings);

  /**
   * Clears any internal caches.
   *
   * Only applicable if the manager makes use of any caching, otherwise
   * it is a no-op.  In caching interfaces, this should cause any
   * retained data to be discarded to ensure future queries are fresh.
   */
  void flushCaches();

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
   * would like to interact with different kinds of entity.
   *
   * This includes the policy for a given trait set, as well as the
   * per-trait policy, with the context for the policy determined by
   * the @p policyAccess.
   *
   * More specifically, depending on the @p policyAccess mode, the
   * response can tell you
   * - Whether the manager is capable of resolving or persisting a
   *   particular kind of entity at all.
   * - Which specific traits can be @ref resolve "resolved", for
   *   existing or future entities.
   * - Which traits can be @ref register_ "persisted" when publishing.
   * - Which traits must have their required properties filled for
   *   publishing to succeed.
   *
   * This allows you to adapt application logic or user-facing behaviour
   * accordingly.
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
   * required trait. Policy is runtime invariant and so only needs to be
   * checked once for any given set of inputs (which includes the
   * @ref Context and its @ref locale).
   *
   * When querying this API, each Trait Set should be composed of:
   *
   *  - The trait set of the entity type in question. This is usually
   *    obtained from the relevant @ref Specification.
   *  - For @fqref{access.PolicyAccess.kRead} "read" usage, any
   *    additional traits with properties that you wish to resolve for
   *    that type of entity.
   *  - For publishing usage, any additional traits with properties that
   *    you wish to publish for that type of entity.
   *
   * Along with the traits that describe the manager's desired
   * interaction pattern (ones with the `managementPolicy` usage
   * metadata), the resulting @fqref{trait.TraitsData} "TraitsData" will
   * be imbued with (potentially a subset of) the requested traits,
   * signalling the manager's capability or requirements for
   * resolving/persisting their properties.
   *
   * The meaning of the subset of traits in the response varies by
   * @p policyAccess mode as follows
   * - @ref access.PolicyAccess.kRead "kRead":  traits that have
   *   properties the manager can @ref resolve from existing entities.
   * - @ref access.PolicyAccess.kWrite "kWrite" and @ref
   *   access.PolicyAccess.kCreateRelated "kCreateRelated": traits that
   *   have properties the manager can persist when @ref publish
   *   "publishing".
   * - @ref access.PolicyAccess.kRequired "kRequired": traits whose
   *   properties must be provided by the host in order for publishing
   *   to succeed.
   * - @ref access.PolicyAccess.kManagerDriven "kManagerDriven": traits
   *   that have properties that the manager can @ref resolve for a
   *   future entity (i.e. an entity reference returned from a @ref
   *   preflight call) that is yet to be @ref register_ "registered".
   *   That is, traits that the manager wishes to drive, rather than
   *   have the host decide.
   *
   * This method gives the global policy for how the manager wishes to
   * interact with certain categories of entity. See @ref entityTraits
   * for entity-specific introspection.
   *
   * @note Because traits are specific to any given application of the
   * API, please refer to the documentation for any relevant companion
   * project(s) that provide traits and specifications for your specific
   * scenario. For example, the
   * <a href="https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation"
   * target="_blank">OpenAssetIO-MediaCreation</a> project provides
   * traits for common data types used in computer graphics and media
   * production. Use the concrete Trait/Specification classes provided
   * by these projects to retrieve data from the supplied
   * trait::TraitsData instead of querying directly using string
   * literals.
   *
   * @note There is no requirement to call this method before any other
   * API interaction, though it is strongly recommended to do so where
   * such information enables high-level behavioural changes or
   * optimisations that improve user experience.
   *
   * @param traitSets The entity @ref trait "traits" to query.
   *
   * @param policyAccess Intended operation type to perform on entities.
   *
   * @param context The calling context.
   *
   * @return a `TraitsData` for each element in @p traitSets.
   */
  [[nodiscard]] trait::TraitsDatas managementPolicy(const trait::TraitSets& traitSets,
                                                    access::PolicyAccess policyAccess,
                                                    const ContextConstPtr& context);

  /**
   * Management Policy queries allow a host to ask a Manager how they
   * would like to interact with different kinds of entity.
   *
   * This includes the policy for a given trait set, as well as the
   * per-trait policy, with the context for the policy determined by
   * the @p policyAccess.
   *
   * See the @ref managementPolicy(const trait::TraitSets&,<!--
   * -->access::PolicyAccess, const ContextConstPtr&) "batch overload"
   * documentation for more details.
   *
   * @param traitSet The entity @ref trait "traits" to query.
   *
   * @param policyAccess Intended operation type to perform on entities.
   *
   * @param context The calling context.
   *
   * @return Policy for the @p traitSet.
   */
  [[nodiscard]] trait::TraitsDataPtr managementPolicy(const trait::TraitSet& traitSet,
                                                      access::PolicyAccess policyAccess,
                                                      const ContextConstPtr& context);
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
   *  empty @fqref{trait.TraitsData} "TraitsData" instance.
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
   *  group, but have different locales or access.
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
   *  @note Using this within the same process to store a context for
   *  use with subsequent API calls or other threads is redundant.
   *  Retain the Context object directly in this situation.
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
   *  supplied here. It does not encode the current locale or other
   *  propeties.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kStatefulContexts.
   *
   * @see @ref Capability.kStatefulContexts
   * @see @ref stable_resolution
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
   * @warning The context's access or locale is not
   * restored by this action.
   *
   * @see @ref stable_resolution
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kStatefulContexts.
   *
   * @see @ref Capability.kStatefulContexts
   *
   * @todo Should we concatenate the manager id in
   * persistenceTokenForContext so we can verify that they match?
   */
  ContextPtr contextFromPersistenceToken(const Str& token);

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
     * containing either a @ref trait::TraitsData or @ref
     * errors.BatchElementError will be provided for each @ref
     * EntityReference provided as an argument to the operation.
     */
    struct Variant {};
    /**
     * Exception policy overloads, when used in a batch context, will
     * emit an exception at the first encountered @ref
     * errors.BatchElementError provided by the @ref ManagerInterface.
     * This exception may not be in index order.
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
   * @fqref{errors.BatchElementError.ErrorCode} "ErrorCode".
   */
  using BatchElementErrorCallback = std::function<void(std::size_t, errors::BatchElementError)>;
  /**
   * @}
   */

  /**
   * @name Entity Reference Inspection
   *
   * Functionality for validating and creating entity references, and
   * the existence or kind of entity that they point to.
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
   * @see @ref entityExists
   * @see @ref resolve
   */
  [[nodiscard]] bool isEntityReferenceString(const Str& someString);

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
   * @throw errors::InputValidationException If the given string is not
   * recognized as an entity reference by this manager.
   *
   * @todo Use a custom exception type rather than std::domain_error.
   */
  [[nodiscard]] EntityReference createEntityReference(Str entityReferenceString);

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
      Str entityReferenceString);

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
   * The supplied context's locale should be well-configured as it
   * may contain information pertinent to disambiguating this subtle
   * definition of 'exists' in some cases too, as it better explains
   * the use-case of the call.
   *
   * @param entityReferences Entity references to query.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful check of an entity reference. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a boolean indicating existence, as defined above. The
   * callback will be called on the same thread that initiated the call
   * to `entityExists`.
   *
   * @param errorCallback Callback that will be called for each
   * failed check of an entity reference. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{errors.BatchElementError}
   * "BatchElementError" (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `entityExists`.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kExistenceQueries.
   *
   * @see @ref Capability.kExistenceQueries
   */
  void entityExists(const EntityReferences& entityReferences, const ContextConstPtr& context,
                    const ExistsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback);

  /**
   * Determines if the supplied @ref entity_reference points to an
   * entity that exists in the @ref asset_management_system.
   *
   * See the documentation for the @ref
   * entityExists(const EntityReferences&, <!--
   * --> const ContextConstPtr&, const ExistsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&) "callback overload" for more
   * details.
   *
   * Errors that occur will be thrown as an exception, either from the
   * @ref manager plugin (for errors not specific to the entity
   * reference) or as a @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference Entity reference to query.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return Boolean indicating existence of the entity.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kExistenceQueries.
   *
   * @see @ref Capability.kExistenceQueries
   */
  bool entityExists(const EntityReference& entityReference, const ContextConstPtr& context,
                    const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Determines if the supplied @ref entity_reference points to an
   * entity that exists in the @ref asset_management_system.
   *
   * See the documentation for the @ref
   * entityExists(const EntityReferences&, <!--
   * --> const ContextConstPtr&, const ExistsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&) "callback overload" for more
   * details.
   *
   * If successful, the result is a boolean indicating the existence of
   * the @ref entity.
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to check the existence of this
   * particular entity.
   *
   * Errors that are not specific to the entity being queried will be
   * thrown as an exception.
   *
   * @param entityReference Entity reference to query.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return Object containing either a boolean indicating the existence
   * of the entity or an error object.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kExistenceQueries.
   *
   * @see @ref Capability.kExistenceQueries
   */
  std::variant<errors::BatchElementError, bool> entityExists(
      const EntityReference& entityReference, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Type to use in place of bool in `vector<bool>` so that the "dynamic
   * bitset" specialisation of std::vector is not used.
   *
   * `std::vector<bool>` is a specialisation that uses a single bit per
   * element, which is more memory efficient but limits the use of
   * the vector for certain operations.
   *
   * As a workaround, we can use an integral type as the vector element,
   * such that zero represents false and non-zero represents true.
   */
  using BoolAsUint = std::uint_fast8_t;

  /**
   * Determines if each supplied @ref entity_reference points to an
   * entity that exists in the @ref asset_management_system.
   *
   * See documentation for the <!--
   * --> @ref entityExists(const EntityReferences&, <!--
   * --> const ContextConstPtr&, const ExistsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback overload" for more details on existence check behaviour.
   *
   * Any errors that occur will be immediately thrown as an exception,
   * either from the @ref manager plugin (for errors not specific to the
   * entity reference) or as a @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences Entity references to query.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of boolean values indicating the existence of each
   * entity.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kExistenceQueries.
   *
   * @see @ref Capability.kExistenceQueries
   */
  std::vector<BoolAsUint> entityExists(
      const EntityReferences& entityReferences, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Determines if each supplied @ref entity_reference points to an
   * entity that exists in the @ref asset_management_system.
   *
   * For successful references, the corresponding element of the result
   * is populated with a boolean indicating the existence of the entity.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to check
   * the existence of that particular entity.
   *
   * Errors that are not specific to an entity will be thrown as an
   * exception, failing the whole batch.
   *
   * See documentation for the <!--
   * --> @ref entityExists(const EntityReferences&, <!--
   * --> const ContextConstPtr&, const ExistsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback overload" for more details on existence check behaviour.
   *
   * @param entityReferences Entity references to query.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either a boolean indicating
   * the existence of the entity or an error.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kExistenceQueries.
   *
   * @see @ref Capability.kExistenceQueries
   */
  std::vector<std::variant<errors::BatchElementError, bool>> entityExists(
      const EntityReferences& entityReferences, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Callback signature used for a successful entity trait set query.
   */
  using EntityTraitsSuccessCallback = std::function<void(std::size_t, trait::TraitSet)>;

  /**
   * Retrieve the @ref trait_set of one or more @ref entity "entities".
   *
   * For example, this may be used to validate that a user-provided
   * entity reference is appropriate for an operation.
   *
   * The trait set returned (via callback) for each @ref
   * entity_reference varies according to the @p entityTraitsAccess
   * access mode.
   *
   * If @ref access.EntityTraitsAccess.kRead "kRead" is given, the
   * response will be an exhaustive trait set for the entity. This may
   * also include traits whose properties the manager is not capable of
   * @ref resolve "resolving", in order to aid categorisation. If an
   * entity does not exist, then the error callback will be invoked
   * using the @ref errors.BatchElementError.ErrorCode.kEntityResolutionError
   * "kEntityResolutionError" code.
   *
   * If @ref access.EntityTraitsAccess.kWrite "kWrite" is given, the
   * response will be the minimal trait set required to categorize the
   * entity during publishing.  This may include traits whose properties
   * the manager is not capable of @ref register_ "persisting". If an
   * entity is read-only, the error callback will be invoked using the
   * @ref errors.BatchElementError.ErrorCode.kEntityAccessError
   * "kEntityAccessError" code.
   *
   * Since the trait set will include all relevant traits for the access
   * mode, not just those with properties that the manager can
   * supply/store, call @ref managementPolicy to determine which of
   * those traits hold properties that can be @ref resolve "resolved" or
   * @ref register_ "persisted".
   *
   * An empty trait set is a valid response, for example if the entity
   * is a new asset with no type constraints.
   *
   * @param entityReferences Entity references to query.
   *
   * @param entityTraitsAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each trait
   * set retrieved for the entity references. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with its @ref trait_set. The callback will be called on the
   * same thread that initiated the call to `entityTraits`.
   *
   * @param errorCallback Callback that will be called for each failure.
   * It will be given the corresponding index of the entity reference in
   * @p entityReferences along with a populated
   * @fqref{errors.BatchElementError} "BatchElementError" (see
   * @fqref{errors.BatchElementError.ErrorCode} "ErrorCodes"). The
   * callback will be called on the same thread that initiated the call
   * to `entityTraits`.
   */
  void entityTraits(const EntityReferences& entityReferences,
                    access::EntityTraitsAccess entityTraitsAccess, const ContextConstPtr& context,
                    const EntityTraitsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback);

  /**
   * Retrieve the @ref trait_set of an @ref entity.
   *
   * See documentation for the <!--
   * --> @ref entityTraits(const EntityReferences&, <!--
   * --> access::EntityTraitsAccess ,const ContextConstPtr&, <!--
   * --> const EntityTraitsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Errors that occur will be thrown as an exception, either from the
   * @ref manager plugin (for errors not specific to the entity
   * reference) or as a @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference Entity reference to query.
   *
   * @param entityTraitsAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return Populated trait set.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   */
  trait::TraitSet entityTraits(const EntityReference& entityReference,
                               access::EntityTraitsAccess entityTraitsAccess,
                               const ContextConstPtr& context,
                               const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @ref trait_set or a
   * @fqref{errors.BatchElementError} "BatchElementError".
   *
   * If successful, the result is populated with the trait set of the
   * @ref entity.
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to retrieve the traits this particular
   * entity.
   *
   * Errors that are not specific to the entity being queried will be
   * thrown as an exception.
   *
   * See documentation for the <!--
   * --> @ref entityTraits(const EntityReferences&, <!--
   * --> access::EntityTraitsAccess, const ContextConstPtr&, <!--
   * --> const EntityTraitsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReference Entity reference to query.
   *
   * @param entityTraitsAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return Object containing either the populated trait set or an
   * error object.
   */
  std::variant<errors::BatchElementError, trait::TraitSet> entityTraits(
      const EntityReference& entityReference, access::EntityTraitsAccess entityTraitsAccess,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Retrieve the @ref trait_set of one or more @ref entity "entities".
   *
   * See documentation for the <!--
   * --> @ref entityTraits(const EntityReferences&, <!--
   * --> access::EntityTraitsAccess, const ContextConstPtr&, <!--
   * --> const EntityTraitsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Any errors that occur will be immediately thrown as an exception,
   * either from the @ref manager plugin (for errors not specific to the
   * entity reference) or as a @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences Entity references to query.
   *
   * @param entityTraitsAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of populated trait sets.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   */
  std::vector<trait::TraitSet> entityTraits(
      const EntityReferences& entityReferences, access::EntityTraitsAccess entityTraitsAccess,
      const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @ref trait_set or a
   * @fqref{errors.BatchElementError} "BatchElementError" for each given
   * @ref entity_reference.
   *
   * For successful references, the corresponding element of the result
   * is populated with its trait set.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * entityTraits that particular entity.
   *
   * Errors that are not specific to an entity will be thrown as an
   * exception, failing the whole batch.
   *
   * See documentation for the <!--
   * --> @ref entityTraits(const EntityReferences&, <!--
   * --> access::EntityTraitsAccess, const ContextConstPtr&, <!--
   * --> const EntityTraitsSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReferences Entity references to query.
   *
   * @param entityTraitsAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either the populated trait
   * set or an error.
   */
  std::vector<std::variant<errors::BatchElementError, trait::TraitSet>> entityTraits(
      const EntityReferences& entityReferences, access::EntityTraitsAccess entityTraitsAccess,
      const ContextConstPtr& context, const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

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
  using ResolveSuccessCallback = std::function<void(std::size_t, trait::TraitsDataPtr)>;

  /**
   * Provides a @fqref{trait.TraitsData} "TraitsData" populated with the
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
   * To determine the @ref trait_set for a particular entity, use @ref
   * entityTraits. Note that this will give a complete trait set,
   * including traits that solely aid classification and whose
   * properties cannot be resolved. See the docs for @ref entityTraits
   * for more information.
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
   * Note that any properties that are defined as being a URL will be
   * URL encoded. If it is expected that trait properties may contain
   * substitution tokens or similar, their convention and behaviour
   * will be defined in the documentation for the respective trait.
   * Consult the originating project of the trait for more information.
   *
   * There may be errors during resolution. These can either be
   * exceptions thrown from `resolve`, or
   * @fqref{errors.BatchElementError} "BatchElementError"s given to the
   * `errorCallback`. Exceptions are unexpected errors that fail the
   * whole batch. `BatchElementError`s are errors that are specific to a
   * particular entity - other entities may still resolve successfully.
   * Using HTTP status codes as an analogy, typically a server error
   * (5xx) would correspond to an exception whereas a client error (4xx)
   * would correspond to a `BatchElementError`.
   *
   * This call will block until all resolutions are complete and
   * callbacks have been called. Callbacks will be called on the
   * same thread that called `resolve`
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param resolveAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful resolution of an entity reference. It will be
   * given the corresponding index of the entity reference in
   * @p entityReferences along with its `TraitsData`. The callback will
   * be called on the same thread that initiated the call to `resolve`.
   *
   * @param errorCallback Callback that will be called for each
   * failed resolution of an entity reference. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{errors.BatchElementError}
   * "BatchElementError" (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `resolve`.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kResolution.
   *
   * @see @ref Capability.kResolution
   */
  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               access::ResolveAccess resolveAccess, const ContextConstPtr& context,
               const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback);

  /**
   * Provides a @fqref{trait.TraitsData} "TraitsData" populated with the
   * available data for the requested set of traits for the given @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, access::ResolveAccess, <!--
   * --> const ContextConstPtr&, const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Errors that occur during resolution will be thrown as an exception,
   * either from the @ref manager plugin (for errors not specific to the
   * entity reference) or as a @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference Entity reference to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied entity
   * reference. Only traits applicable to the supplied entity reference
   * will be set in the resulting data.
   *
   * @param resolveAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return Populated data.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kResolution.
   *
   * @see @ref Capability.kResolution
   */
  trait::TraitsDataPtr resolve(const EntityReference& entityReference,
                               const trait::TraitSet& traitSet,
                               access::ResolveAccess resolveAccess, const ContextConstPtr& context,
                               const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @fqref{trait.TraitsData} "TraitsData"
   * or a @fqref{errors.BatchElementError} "BatchElementError".
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
   * --> const trait::TraitSet&, access::ResolveAccess, <!--
   * --> const ContextConstPtr&, const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReference Entity reference to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied entity
   * reference. Only traits applicable to the supplied entity reference
   * will be set in the resulting data.
   *
   * @param resolveAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return Object containing either the populated data or an error
   * object.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kResolution.
   *
   * @see @ref Capability.kResolution
   */
  std::variant<errors::BatchElementError, trait::TraitsDataPtr> resolve(
      const EntityReference& entityReference, const trait::TraitSet& traitSet,
      access::ResolveAccess resolveAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Provides a @fqref{trait.TraitsData} "TraitsData" populated with the
   * available data for the requested set of traits for each given @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref resolve(const EntityReferences&, <!--
   * --> const trait::TraitSet&, access::ResolveAccess, <!--
   * --> const ContextConstPtr&, const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * Any errors that occur during resolution will be immediately thrown
   * as an exception, either from the @ref manager plugin (for errors
   * not specific to the entity reference) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param resolveAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of populated data objects.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kResolution.
   *
   * @see @ref Capability.kResolution
   */
  std::vector<trait::TraitsDataPtr> resolve(
      const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
      access::ResolveAccess resolveAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Provides either a populated @fqref{trait.TraitsData} "TraitsData"
   * or a @fqref{errors.BatchElementError} "BatchElementError" for each
   * given @ref entity_reference.
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
   * --> const trait::TraitSet&, access::ResolveAccess, <!--
   * --> const ContextConstPtr&, const ResolveSuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback)
   * "callback variation" for more details on resolution behaviour.
   *
   * @param entityReferences Entity references to query.
   *
   * @param traitSet The trait IDs to resolve for the supplied list of
   * entity references. Only traits applicable to the supplied entity
   * references will be set in the resulting data.
   *
   * @param resolveAccess The intended usage of the data.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either the populated data
   * or an error.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kResolution.
   *
   * @see @ref Capability.kResolution
   */
  std::vector<std::variant<errors::BatchElementError, trait::TraitsDataPtr>> resolve(
      const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
      access::ResolveAccess resolveAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Callback signature used for a successful default entity reference query.
   */
  using DefaultEntityReferenceSuccessCallback =
      std::function<void(std::size_t, std::optional<EntityReference>)>;

  /**
   * Called to determine an @ref EntityReference considered to be a
   * sensible default for each of the given entity @ref trait_set
   * "trait sets" and context.
   *
   * This can be used to ensure dialogs, prompts or publish locations
   * default to some sensible value, avoiding the need for a user to
   * re-enter such information. There may be situations where there is
   * no meaningful default, so the caller should be robust to this
   * situation.
   *
   * @param traitSets  The relevant trait sets for the type of entities
   * required, these will be interpreted in conjunction with the context
   * to determine the most sensible default.
   *
   * @param defaultEntityAccess Intended usage of the returned entity
   * reference(s).
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful default retrieved for each of the given sets in @p
   * traitSets. It will be given the corresponding index of the trait
   * set in @p traitSets along with the default entity reference. If the
   * query is well-formed, but there is no available default entity
   * reference, then the `optional` entity reference will not contain a
   * value. The callback will be called on the same thread that
   * initiated the call to `defaultEntityReference`.
   *
   * @param errorCallback Callback that will be called for each failure
   * to retrieve a sensible default entity reference. It will be given
   * the corresponding index for each of the given sets in @p traitSets
   * along with a populated @fqref{errors.BatchElementError}
   * "BatchElementError" (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The
   * @fqref{errors.BatchElementError.ErrorCode.kEntityAccessError}
   * "kEntityAccessError" error will be used if no suitable default
   * reference exists, and the
   * @fqref{errors.BatchElementError.ErrorCode.kInvalidTraitSet}
   * "kInvalidTraitSet" error will be used if the requested trait set is
   * not recognised by the manager. The callback will be called on the
   * same thread that initiated the call to `defaultEntityReference`.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kDefaultEntityReferences.
   *
   * @see @ref Capability.kDefaultEntityReferences
   */
  void defaultEntityReference(const trait::TraitSets& traitSets,
                              access::DefaultEntityAccess defaultEntityAccess,
                              const ContextConstPtr& context,
                              const DefaultEntityReferenceSuccessCallback& successCallback,
                              const BatchElementErrorCallback& errorCallback);

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
   * In the this API, these relationships are represented by trait data.
   * This may just compose property-less traits as a 'type', or
   * additionally, set trait property values to further define the
   * relationship. For example in the case of AOVs, the type might be
   * 'alternate output' and the attributes may be that the 'channel' is
   * 'diffuse'.
   *
   * Related references form a vital part in the abstraction of the
   * internal structure of the asset management system from the host
   * application in its attempts to provide the user with meaningful
   * functionality. A good example of this is in an editorial workflow,
   * where you may need to query whether a 'shot' exists in a certain
   * part of the asset system. One approach would be to use a
   * 'getChildren' call, on this part of the system. This has the
   * drawback that is assumes that shots are always something that can
   * be described as 'immediate children' of the location in question.
   * This may not always be the case (say, for example there is some
   * kind of 'task' structure in place too). Instead we use a request
   * that asks for any 'shots' that relate to the chosen location. It is
   * then up to the implementation of the manager to determine how that
   * maps to its own data model. Hopefully this allows a host to work
   * with a broader range of asset management systems, without providing
   * any requirements of their structure or data model within the system
   * itself.
   *
   * @{
   */

  /**
   * Callback signature used for a successful paged entity relationship
   * query.
   */
  using RelationshipQuerySuccessCallback =
      std::function<void(std::size_t, EntityReferencePagerPtr)>;

  /**
   * Query for entity references that are related to the input
   * references by the relationship defined by a set of traits and
   * their properties.
   *
   * This is an essential function in this API - as it is widely used
   * to query other entities or organisational structure.
   *
   * When calling this method, you can expect to receive one result
   * per @ref entity_reference provided.
   *
   * @note Consult the documentation for the relevant relationship
   * traits to determine if the order of entities in the inner lists
   * of matching references is considered meaningful.
   *
   * If any relationship definition is unknown, then an empty list
   * will be returned for that entity, and no errors will be
   * raised.
   *
   * @param entityReferences A list of @ref entity_reference to query
   * the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful relationship query. It will be given the corresponding
   * index of the entity reference in @p entityReferences as well as a
   * pager capable of returning pages of entities that have the
   * relationship to the entity at the corresponding index, specified by
   * @p relationshipTraitsData. If there are no relations, the pager
   * will have no pages. The callback will be called on the same thread
   * that initiated the call to `getWithRelationship`. To access
   * the data, retrieve the @ref EntityReferencePager from the callback,
   * and use its interface to traverse pages.
   *
   * @param errorCallback Callback that will be called for each failed
   * relationship query. It will be given the corresponding index of the
   * entity reference in @p entityReferences along with a populated
   * BatchElementError (see @ref errors.BatchElementError.ErrorCode
   * "ErrorCodes"). The callback will be called on the same thread that
   * initiated the call to `getWithRelationship`.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  void getWithRelationship(const EntityReferences& entityReferences,
                           const trait::TraitsDataPtr& relationshipTraitsData, size_t pageSize,
                           access::RelationsAccess relationsAccess, const ContextConstPtr& context,
                           const RelationshipQuerySuccessCallback& successCallback,
                           const BatchElementErrorCallback& errorCallback,
                           const trait::TraitSet& resultTraitSet = {});

  /**
   * Query for entity references that are related to the input
   * reference by the relationship defined by a set of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationship(const EntityReferences&, <!--
   * --> const trait::TraitsDataPtr&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * Any errors that occur during the query will be immediately thrown
   * as an exception, either from the @ref manager plugin (for errors
   * not specific to the entity relationship) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference An @ref entity_reference to query
   * the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return @ref EntityReferencePager pointer. Pages over
   * an unbounded set of entity references related to the input
   * entity reference.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  EntityReferencePagerPtr getWithRelationship(
      const EntityReference& entityReference, const trait::TraitsDataPtr& relationshipTraitsData,
      size_t pageSize, access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const trait::TraitSet& resultTraitSet,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Query for entity references that are related to the input
   * reference by the relationship defined by a set of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationship(const EntityReferences&, <!--
   * --> const trait::TraitsDataPtr&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * If successful, the result is populated with an
   * EntityReferencePager, which pages over an unbounded set of entity
   * references related to the input entity reference, or an error.
   *
   * Otherwise, the result is populated with an error object detailing
   * the reason for the failure to fetch the related entities.
   *
   * Errors that are not specific to the entity relationship will be
   * thrown as an exception.
   *
   * @param entityReference An @ref entity_reference to query
   * the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return Object containing either the EntityReferencePager pointer,
   * which pages over an unbounded set of entity references related to
   * the input entity reference, or an error.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  std::variant<errors::BatchElementError, EntityReferencePagerPtr> getWithRelationship(
      const EntityReference& entityReference, const trait::TraitsDataPtr& relationshipTraitsData,
      size_t pageSize, access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const trait::TraitSet& resultTraitSet,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Query for entity references that are related to the input
   * references by the relationship defined by a set of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationship(const EntityReferences&, <!--
   * --> const trait::TraitsDataPtr&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * Any errors that occur during the query will be immediately thrown
   * as an exception, either from the @ref manager plugin (for errors
   * not specific to the entity relationship) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences A list of @ref entity_reference to query
   * the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of @ref EntityReferencePager pointers. These page over
   * unbounded sets of entity references related to the input
   * entity references.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  std::vector<EntityReferencePagerPtr> getWithRelationship(
      const EntityReferences& entityReferences, const trait::TraitsDataPtr& relationshipTraitsData,
      size_t pageSize, access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const trait::TraitSet& resultTraitSet,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Query for entity references that are related to the input
   * references by the relationship defined by a set of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationship(const EntityReferences&, <!--
   * --> const trait::TraitsDataPtr&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * For successful relationships, the corresponding element of the
   * result is populated with an EntityReferencePager, which pages over
   * an unbounded set of entity references related to the corresponding
   * input entity reference.
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * fetch the related entities for that particular relationship.
   *
   * Errors that are not specific to an entity relationship will be
   * thrown as an exception, failing the whole batch.
   *
   * @param entityReferences A list of @ref entity_reference to query
   * the specified relationship for.
   *
   * @param relationshipTraitsData The traits of the relationship to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either the
   * EntityReferencePager pointer, which pages over an unbounded set of
   * entity references related to the input entity reference, or an
   * error.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>>
  getWithRelationship(const EntityReferences& entityReferences,
                      const trait::TraitsDataPtr& relationshipTraitsData, size_t pageSize,
                      access::RelationsAccess relationsAccess, const ContextConstPtr& context,
                      const trait::TraitSet& resultTraitSet,
                      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * Query for entity references that are related to the input reference
   * by the relationships defined by sets of traits and their
   * properties.
   *
   * This is an essential function in this API - as it is widely used to
   * query other entities or organisational structure.
   *
   * @note Consult the documentation for the relevant relationship
   * traits to determine if the order of entities in the inner lists of
   * matching references is considered meaningful.
   *
   * When calling this method, you can expect to receive one result
   * per relationship provided in @p relationshipTraitsDatas.
   *
   * If any relationship definition is unknown, then an empty list will
   * be returned for that relationship, and no errors will be raised.
   *
   * @param entityReference The @ref entity_reference to query the
   * specified relationships for.
   *
   * @param relationshipTraitsDatas The traits of the relationships to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful relationship query. It will be given the corresponding
   * index of the relationship in @p relationshipTraitsDatas as well as
   * a pager capable of returning pages of entities related to @p
   * entityReference by the relationship at that corresponding index. If
   * there are no relations, the pager will have no pages. The callback
   * will be called on the same thread that initiated the call to
   * `getWithRelationships`. To access the data, retrieve the
   * @ref EntityReferencePager from the callback, and use its interface
   * to traverse pages.
   *
   * @param errorCallback Callback that will be called for each failed
   * relationship query. It will be given the corresponding index of the
   * relationship in @p relationshipTraitsDatas along with a populated
   * BatchElementError (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread that
   * initiated the call to `getWithRelationships`.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @note The @ref trait_set of any queried relationship can be passed
   * to @ref managementPolicy in order to determine if the manager
   * handles relationships of that type.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  void getWithRelationships(const EntityReference& entityReference,
                            const trait::TraitsDatas& relationshipTraitsDatas, size_t pageSize,
                            access::RelationsAccess relationsAccess,
                            const ContextConstPtr& context,
                            const RelationshipQuerySuccessCallback& successCallback,
                            const BatchElementErrorCallback& errorCallback,
                            const trait::TraitSet& resultTraitSet = {});

  /**
   * Query for entity references that are related to the input
   * reference by the relationships defined by sets of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationships(const EntityReference&, <!--
   * --> const trait::TraitsDatas&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * Any errors that occur during the query will be immediately thrown
   * as an exception, either from the @ref manager plugin (for errors
   * not specific to the entity relationship) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference The @ref entity_reference to query the
   * specified relationships for.
   *
   * @param relationshipTraitsDatas The traits of the relationships to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Exception.
   *
   * @return List of @ref EntityReferencePager pointers. These page over
   * unbounded sets of entity references related to the input
   * entity reference.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  std::vector<EntityReferencePagerPtr> getWithRelationships(
      const EntityReference& entityReference, const trait::TraitsDatas& relationshipTraitsDatas,
      size_t pageSize, access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const trait::TraitSet& resultTraitSet,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Query for entity references that are related to the input
   * reference by the relationships defined by sets of traits and
   * their properties.
   *
   * See documentation for the <!--
   * --> @ref getWithRelationships(const EntityReference&, <!--
   * --> const trait::TraitsDatas&, size_t, <!--
   * --> access::RelationsAccess, const ContextConstPtr&, <!--
   * --> const RelationshipQuerySuccessCallback&, <!--
   * --> const BatchElementErrorCallback& errorCallback, <!--
   * --> const trait::TraitSet&)
   * "callback variation" for more details on relationship behaviour.
   *
   * For successful relationships, the corresponding element of the
   * result is populated with an EntityReferencePager, which pages over
   * an unbounded set of entity references related to the corresponding
   * input entity reference
   *
   * Otherwise, the corresponding element of the result is populated
   * with an error object detailing the reason for the failure to
   * fetch the related entities for that particular relationship.
   *
   * Errors that are not specific to an entity relationship will be
   * thrown as an exception, failing the whole batch.
   *
   * @param entityReference The @ref entity_reference to query the
   * specified relationships for.
   *
   * @param relationshipTraitsDatas The traits of the relationships to
   * query.
   *
   * @param pageSize The size of each page of data. The page size is
   * fixed for the lifetime of pager object given to the @p
   * successCallback. Must be greater than zero.
   *
   * @param relationsAccess The intended usage of the returned
   * references.
   *
   * @param context The calling context.
   *
   * @param resultTraitSet A hint as to what traits the returned
   * entities should have.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tagged dispatch idiom). See @ref
   * BatchElementErrorPolicyTag::Variant.
   *
   * @return List of objects, each containing either the
   * EntityReferencePager pointer, which pages over an unbounded set of
   * entity references related to the input entity reference, or an error.
   *
   * @throws errors.InputValidationException if @p pageSize is zero.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kRelationshipQueries.
   *
   * @see @ref Capability.kRelationshipQueries
   */
  std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>>
  getWithRelationships(const EntityReference& entityReference,
                       const trait::TraitsDatas& relationshipTraitsDatas, size_t pageSize,
                       access::RelationsAccess relationsAccess, const ContextConstPtr& context,
                       const trait::TraitSet& resultTraitSet,
                       const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /// @}

  /**
   * @name Publishing
   *
   * The publishing functions allow the host to create or update an @ref
   * entity within the @ref asset_management_system represented by the
   * Manager. The API is designed to accommodate the broad variety of
   * roles that different asset managers embody. Some are 'librarians'
   * that simply catalog the locations of existing media. Others take an
   * active role in both the temporary and long-term paths to items they
   * manage.
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
   * meaningful reference given the @fqref{trait.TraitsData}
   * "TraitsData" of the entity that is being created or published.
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
   * The action of 'publishing' itself, is split into two parts,
   * depending on the nature of the item to be published.
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
   * avoid confusion, this API provides the @ref updateTerminology
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
   * It should be called before register_() if you are about to
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
   * @note If the supplied @fqref{trait.TraitsData} "trait data" is
   * missing traits or properties required by the manager for any input
   * entity reference, then that element will error. See @ref
   * glossary_preflight "glossary entry" for details.
   *
   * The @ref entityTraits method may be used to determine the minimal
   * @ref trait_set required for publishing. Note that the manager may
   * not persist all trait properties in the given set, they may be
   * required solely for classification. See @ref entityTraits docs for
   * more information.
   *
   * @warning The working @ref entity_reference returned by this
   * method should *always* be used in place of the original
   * reference supplied to `preflight` for resolves prior to
   * registration, and for the final call to @ref
   * register_ itself. See @ref example_publishing_a_file.
   *
   * @param entityReferences The entity references to preflight prior
   * to registration.
   *
   * @param traitsHints @ref trait_set for each entity, determining the
   * type of entity to publish, complete with any properties the host
   * owns and can provide at this time. See @ref glossary_preflight
   * "glossary entry" for details.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity.
   *
   * @param context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful preflight of an entity reference. It will be given
   * the corresponding index of the entity reference in
   * @p entityReferences along with an updated reference to use for
   * future interactions as part of the publishing operation. The
   * callback will be called on the same thread that initiated the
   * call to `preflight`.
   *
   * @param errorCallback Callback that will be called for each
   * failed preflight of an entity reference. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{errors.BatchElementError}
   * "BatchElementError" (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `preflight`.
   *
   * @see @ref register_
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  void preflight(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsHints,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback);

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to a supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on preflight behaviour.
   *
   * Any errors that occur during the preflight call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference The entity reference to preflight prior
   * to registration.
   *
   * @param traitsHint @ref trait_set for the entity,
   * determining the type of entity to publish, complete with any
   * properties that can be provided at this time.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity.
   *
   * @param context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions as part of
   * the publishing operation
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  EntityReference preflight(const EntityReference& entityReference,
                            const trait::TraitsDataPtr& traitsHint,
                            access::PublishingAccess publishingAccess,
                            const ContextConstPtr& context,
                            const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to a supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const PreflightSuccessCallback&, <!--
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
   * @param traitsHint @ref trait_set for the entity,
   * determining the type of entity to publish, complete with any
   * properties that can be provided at this time.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity.
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
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  std::variant<errors::BatchElementError, EntityReference> preflight(
      const EntityReference& entityReference, const trait::TraitsDataPtr& traitsHint,
      access::PublishingAccess publishingAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to each supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const PreflightSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on preflight behaviour.
   *
   * Any errors that occur during the preflight call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to an entity reference) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences The entity references to preflight prior
   * to registration.
   *
   * @param traitsHints @ref trait_set for each entity,
   * determining the type of entity to publish, complete with any
   * properties that can be provided at this time.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity.
   *
   * @param context The calling context. The same calling context is
   * used for each entity reference.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated references to use for future interactions as part
   * of the publishing operation
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  EntityReferences preflight(const EntityReferences& entityReferences,
                             const trait::TraitsDatas& traitsHints,
                             access::PublishingAccess publishingAccess,
                             const ContextConstPtr& context,
                             const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * This call signals your intent as a host application to do some
   * work to create data in relation to each supplied @ref
   * entity_reference.
   *
   * See documentation for the <!--
   * --> @ref preflight(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const PreflightSuccessCallback&, <!--
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
   * @param traitsHints @ref trait_set for each entity,
   * determining the type of entity to publish, complete with any
   * properties that can be provided at this time.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity.
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
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  std::vector<std::variant<errors::BatchElementError, EntityReference>> preflight(
      const EntityReferences& entityReferences, const trait::TraitsDatas& traitsHints,
      access::PublishingAccess publishingAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

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
   * The @ref entityTraits method may be used to determine the minimal
   * @ref trait_set required for publishing. Note that the manager may
   * not persist all trait properties in the given set, they may be
   * required solely for classification. See @ref entityTraits docs for
   * more information.
   *
   * As each @ref entity_reference has (ultimately) come from the
   * manager (either in response to delegation of UI/etc... or as a
   * return from another call), then it can be assumed that the
   * Manager will understand what it means for you to call `register`
   * on this reference with the supplied @fqref{trait.TraitsData}
   * "TraitsData". The conceptual meaning of the call is:
   *
   * "I have this reference you gave me, and I would like to register
   * a new entity to it with the traits I told you about before. I
   * trust that this is ok, and you will give me back the reference
   * that represents the result of this."
   *
   * It is up to the manager to understand the correct result for the
   * particular trait set in relation to this reference. For example, if
   * you received this reference in response to browsing for a target to
   * `kWrite` and the traits of a `ShotSpecification`, then the Manager
   * should have returned you a reference that you can then register a
   * `ShotSpecification` entity to without error. The resulting entity
   * reference should then reference the newly created Shot.
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
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity. Note that if the @p entityReference came from a
   * @ref preflight call, then @fqref{access.PublishAccess.kWrite}
   * "kWrite" is the only valid value here.
   *
   * @param context Context The calling context.
   *
   * @param successCallback Callback that will be called for each
   * successful registration of an entity reference. It will be given
   * the corresponding index of the entity reference in
   * @p entityReferences along with an updated reference to use for
   * future interactions with the resulting new entity. The callback
   * will be called on the same thread that initiated the call to
   * `register`.
   *
   * @param errorCallback Callback that will be called for each
   * failed registration of an entity reference. It will be given the
   * corresponding index of the entity reference in @p entityReferences
   * along with a populated @fqref{errors.BatchElementError}
   * "BatchElementError" (see @fqref{errors.BatchElementError.ErrorCode}
   * "ErrorCodes"). The callback will be called on the same thread
   * that initiated the call to `register`.
   *
   * @throws std::out_of_range If @p entityReferences and
   * @p entityTraitsDatas are not lists of the same length.
   * Other exceptions may be raised for fatal runtime errors, for
   * example server communication failure.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @fqref{trait.TraitsData} "TraitsData"
   * @see @ref preflight
   * @see @ref Capability.kPublishing
   *
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  void register_(const EntityReferences& entityReferences,
                 const trait::TraitsDatas& entityTraitsDatas,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback);

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * Any errors that occur during the register_ call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReference Entity reference to register to.
   *
   * @param entityTraitsData The data to register for the entity.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity. Note that if the @p entityReference came from a
   * @ref preflight call, then @fqref{access.PublishAccess.kWrite}
   * "kWrite" is the only valid value here.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions with the
   * resulting new entity.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  EntityReference register_(const EntityReference& entityReference,
                            const trait::TraitsDataPtr& entityTraitsData,
                            access::PublishingAccess publishingAccess,
                            const ContextConstPtr& context,
                            const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const RegisterSuccessCallback&, <!--
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
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity. Note that if the @p entityReference came from a
   * @ref preflight call, then @fqref{access.PublishAccess.kWrite}
   * "kWrite" is the only valid value here.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated reference to use for future interactions with the
   * resulting new entity or an error object detailing the reason for
   * the failure of this particular entity.
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::variant<errors::BatchElementError, EntityReference> register_(
      const EntityReference& entityReference, const trait::TraitsDataPtr& entityTraitsData,
      access::PublishingAccess publishingAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);
  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const RegisterSuccessCallback&, <!--
   * --> const BatchElementErrorCallback&)
   * "callback variation" for more details on register_ behaviour.
   *
   * Any errors that occur during the register_ call will be immediately
   * thrown as an exception, either from the @ref manager plugin (for
   * errors not specific to the entity reference) or as a
   * @fqref{errors.BatchElementException}
   * "BatchElementException"-derived error.
   *
   * @param entityReferences Entity references to register to.
   *
   * @param entityTraitsDatas The data to register for each entity.
   * NOTE: All supplied instances should have the same trait set,
   * batching with varying traits is not supported.
   *
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity. Note that if the @p entityReference came from a
   * @ref preflight call, then @fqref{access.PublishAccess.kWrite}
   * "kWrite" is the only valid value here.
   *
   * @param context Context The calling context.
   *
   * @param errorPolicyTag  Parameter for selecting the appropriate
   * overload (tag dispatch idiom). See @ref BatchElementErrorPolicyTag.
   *
   * @return Updated references to use for future interactions with the
   * resulting new entities.
   *
   * @throws errors.BatchElementException Converted exception thrown
   * when the manager emits a @fqref{errors.BatchElementError}
   * "BatchElementError".
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::vector<EntityReference> register_(
      const EntityReferences& entityReferences, const trait::TraitsDatas& entityTraitsDatas,
      access::PublishingAccess publishingAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Exception& errorPolicyTag = {});

  /**
   * Register should be used to 'publish' new entities either when
   * originating new data within the application process, or
   * referencing some existing file, media or information.
   *
   * See documentation for the <!--
   * --> @ref register_(const EntityReferences&, <!--
   * --> const trait::TraitsDatas&, access::PublishingAccess, <!--
   * --> const ContextConstPtr&, const RegisterSuccessCallback&, <!--
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
   * @param publishingAccess Whether to perform a generic
   * @fqref{access.PublishAccess.kWrite} "write" to an entity or to
   * (explicitly) @fqref{access.PublishAccess.kCreateRelated} "create a
   * related" entity. Note that if the @p entityReference came from a
   * @ref preflight call, then @fqref{access.PublishAccess.kWrite}
   * "kWrite" is the only valid value here.
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
   *
   * @throws errors.NotImplementedException Thrown when this method is
   * not implemented by the manager. Check that this method is
   * implemented before use by calling @ref hasCapability with @ref
   * Capability.kPublishing.
   *
   * @see @ref Capability.kPublishing
   */
  // NOLINTNEXTLINE(readability-identifier-naming)
  std::vector<std::variant<errors::BatchElementError, EntityReference>> register_(
      const EntityReferences& entityReferences, const trait::TraitsDatas& entityTraitsDatas,
      access::PublishingAccess publishingAccess, const ContextConstPtr& context,
      const BatchElementErrorPolicyTag::Variant& errorPolicyTag);

  /// @}

 private:
  explicit Manager(managerApi::ManagerInterfacePtr managerInterface,
                   managerApi::HostSessionPtr hostSession);

  managerApi::ManagerInterfacePtr managerInterface_;
  managerApi::HostSessionPtr hostSession_;

  std::optional<openassetio::Str> entityReferencePrefix_;
};
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
