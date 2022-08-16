// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <optional>
#include <string>

#include <openassetio/export.h>
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
   * supplied traits through @needsref resolve and @needsref register.
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
   * @see @needsref resolve
   *
   * @todo Make use of
   * openassetio.constants.kField_EntityReferencesMatchPrefix if
   * supplied, especially when bridging between C/python.
   */
  [[nodiscard]] bool isEntityReferenceString(const std::string& someString) const;

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

 private:
  explicit Manager(managerApi::ManagerInterfacePtr managerInterface,
                   managerApi::HostSessionPtr hostSession);

  managerApi::ManagerInterfacePtr managerInterface_;
  managerApi::HostSessionPtr hostSession_;
};
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
