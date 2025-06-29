// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <optional>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/access.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateStateInterface)
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateRequest)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

OPENASSETIO_DECLARE_PTR(UIDelegateInterface)

/**
 * This interface binds the @ref glossary_UI_Delegate of an @ref
 * asset_management_system into OpenAssetIO.
 *
 * It is not called directly by a @ref host, but by the middleware that
 * presents a more object-oriented model of this to the @ref host -
 * namely, the @fqref{ui.hostApi.UIDelegate} "UIDelegate".
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
 * @see @fqref{managerApi.HostSession.logger} "HostSession.logger"
 * @see @fqref{log.LoggerInterface} "LoggerInterface"
 *
 * Exceptions should be thrown to handle any in-flight errors that
 * occur. The error should be mapped to a derived class of
 * @ref errors.OpenAssetIOException, and thrown.  All exceptions of this
 * kind will be correctly passed across the plug-in C boundary,
 * and re-thrown. Other exceptions should not be used.
 *
 *  @see @fqref{errors} "errors"
 *
 * Hosts
 * -----
 *
 * Sometimes you may need to know more information about the API host.
 * A @fqref{managerApi.Host} "Host" object is available through the
 * @fqref{managerApi.HostSession} "HostSession" object passed to each
 * method of this class. This provides a standardised interface that all
 * API hosts guarantee to implement. This can be used to identify
 * exactly which host you are being called for, and query various entity
 * related specifics of the hosts data model.
 *
 * @see @fqref{managerApi.Host} "Host"
 *
 * Initialization
 * --------------
 *
 * The constructor makes a new instance, but at this point it is not
 * ready for use. Instances of this class should be lightweight to
 * create, but don't have to be lightweight to initialize. The
 * informational methods must be available pre-initialization, so that
 * queries can be made relatively cheaply to provide users with a list
 * of UI delegates and their settings. None of the UI-related methods
 * will be called until after @ref initialize has been called. The
 * following methods must be callable prior to initialization:
 *
 *    @li @ref identifier()
 *    @li @ref displayName()
 *    @li @ref info()
 *    @li @ref settings()
 *
 * @see @ref initialize
 *
 * @note OpenAssetIO makes use of shared pointers to facilitate object
 * lifetime management across multiple languages. Instances passed into
 * API methods via shared pointer may have their lifetimes extended
 * beyond that of your code.
 */
class OPENASSETIO_UI_EXPORT UIDelegateInterface {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateInterface)

  using HostSessionPtr = openassetio::managerApi::HostSessionPtr;

  UIDelegateInterface();

  /**
   * Polymorphic destructor.
   */
  virtual ~UIDelegateInterface() = default;

  /**
   * @name UI Delegate Identification
   *
   * These functions provide hosts with general identity information
   * about the UI delegate itself. These may all be
   * called before @ref initialize has been called.
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify a specific UI delegate.
   *
   * @note This must match the identifier of the corresponding @ref
   * glossary_manager_plugin.
   *
   * The UI delegate will typically be instantiated using settings from
   * the same configuration file as is used for the manager plugin, and
   * so expect the same identifier as the manager plugin.
   *
   * @see @ref hostApi.UIDelegateFactory.defaultUIDelegateForInterface
   *
   * @return Unique identifier of the UI delegate.
   *
   * @see @fqref{managerApi.ManagerInterface.identifier}
   * "ManagerInterface.identifier".
   */
  [[nodiscard]] virtual Str identifier() const = 0;

  /**
   * Returns a human-readable name to be used to reference this
   * specific UI delegate in user-facing messaging.
   *
   * One instance of its use may be in a host's preferences UI or
   * logging. For example:
   *
   *     "OpenAssetIO Test Manager UI"
   *
   * @return UI delegate's display name.
   */
  [[nodiscard]] virtual Str displayName() const = 0;

  /**
   * @}
   */

  /**
   * Returns other information that may be useful about this UI
   * delegate. This can contain arbitrary key/value
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
   * The @ref constants.kInfoKey_IsPython constant is used to signal to
   * the host that the UI delegate is written in Python, and therefore
   * any @ref UIDelegateRequest.nativeData and @ref
   * UIDelegateStateInterface.nativeData will/must be a CPython
   * `PyObject*`. The @ref
   * openassetio.ui.managerApi.UIDelegateInterface.UIDelegateInterface.info
   * "Python base class implementation" sets `kInfoKey_IsPython: True`.
   *
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] virtual InfoDictionary info();

  /**
   * @name Initialization
   *
   * @{
   */

  /**
   * Retrieve settings currently applied to this UI delegate.
   *
   * @param hostSession The API session.
   *
   * @return Any settings relevant to the function of the UI delegate
   * with their current values (or their defaults if @ref initialize has
   * not yet been called).
   *
   * The default implementation returns an empty dictionary.
   */
  [[nodiscard]] virtual InfoDictionary settings(const HostSessionPtr& hostSession);

  /**
   * Prepares for interaction with a host.
   *
   * This method is passed a settings dictionary, that can be used to
   * configure required local state to service requests. For example,
   * determining the authoritative back-end service managing asset data.
   * This is also a good opportunity to initialize any connections or
   * fetch pre-requisite data. It is fine for this call to block for a
   * period of time.
   *
   * If an exception is raised by this call, it signifies to the host
   * that a fatal error occurred, and this UI delegate is not available
   * with the current settings.
   *
   * If no exception is raised, it can be assumed that the UI delegate
   * is ready. It is the implementations responsibility to deal with
   * transient connection errors (if applicable) once initialized.
   *
   * If called on an already initialized instance, re-initialize with
   * any updated settings that are provided. If an error was raised
   * previously, then initialization should be re-attempted.
   *
   * @note This will always be called prior to any UI related calls. An
   * exception should be raised if this is not the case. However,
   * the following functions may be called prior to initialization:
   *
   *  @li @ref identifier()
   *  @li @ref displayName()
   *  @li @ref info()
   *  @li @ref settings()
   *
   * @param uiDelegateSettings Settings to apply to the UI delegate on
   * initialisation.
   *
   * @param hostSession The API session.
   */
  virtual void initialize(InfoDictionary uiDelegateSettings, const HostSessionPtr& hostSession);

  /**
   * Dispose of all active references to delegated UI.
   *
   * Called automatically on destruction of the @ref hostApi.UIDelegate
   * middleware in use by the host, but the host may call this
   * independently in order to re-use this instance.
   *
   * @warning When this is called during destruction of a Python @ref
   * hostApi.UIDelegate instance, the Python GIL will be held for the
   * duration of the call.
   *
   * Any UI elements created by this UI delegate should be considered
   * unsafe for access when this method is called. Any dangling state
   * should be cleaned up to prevent memory leaks and/or potential
   * access to destroyed objects.
   *
   * The default implementation is a no-op.
   *
   * @param hostSession The API session.
   */
  virtual void close(const HostSessionPtr& hostSession);

  /**
   * @}
   */

  /**
   * @name Policy
   *
   * @{
   */

  /**
   * Retrieve the policy for UI delegation with respect to different
   * kinds of UI request.
   *
   * The set of UI-specific traits indicates the kind of UI element
   * requested, and the access mode determines if the request is for
   * a read or publishing operation.
   *
   * A return value of an empty @ref trait.TraitsData "TraitsData"
   * indicates to the host that UI delegation requests of this kind are
   * not supported, and it should not attempt @ref populateUI calls with
   * these arguments.
   *
   * This method is usually called early on by a host to determine
   * whether to attempt to present OpenAssetIO related UI elements to
   * the user, and to retrieve other sundry UI related metadata that is
   * not specific to an individual request.
   *
   * Note that even if this method returns positively, @ref populateUI
   * may refuse to provide a UI element, based on the specific request.
   *
   * Consult the relevant traits library to discover the available
   * UI policy-specific traits. For example, the
   * <a href="https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation"
   * target="_blank">OpenAssetIO-MediaCreation</a> project provides
   * traits related to computer graphics and media production. In
   * particular, imbuing the return value with the `Managed` UI policy
   * trait from the MediaCreation library indicates to the host that UI
   * delegation requests are likely to succeed.
   *
   * As well as determining whether a request is likely to be supported,
   * additional metadata that may be used by the host can be populated
   * in the returned @ref trait.TraitsData "TraitsData". For example,
   * this could include a "display name" that the host may use in the
   * titles of tabs or windows that contain the delegated UI element(s).
   *
   * This method is opt-in - hosts may call @ref populateUI without
   * first consulting this method. It is therefore important that
   * correct behaviour is not reliant on this method being called. Any
   * additional metadata offered in the returned policy may be useful in
   * optimising the user experience, but cannot be considered a
   * requirement.
   *
   * @param uiTraitSet The set of UI-specific @ref trait "traits"
   * determining the kind of UI element the host may wish to delegate.
   *
   * @param uiAccess Type of operation that the delegated UI will be
   * used for.
   *
   * @param context The calling context.
   *
   * @param hostSession The API session.
   *
   * @return Policy-specific traits with their associated properties
   * filled, if applicable. The default implementation returns an empty
   * response, indicating UI delegation is not supported.
   */
  virtual trait::TraitsDataPtr uiPolicy(const trait::TraitSet& uiTraitSet,
                                        access::UIAccess uiAccess, const ContextConstPtr& context,
                                        const HostSessionPtr& hostSession);

  /**
   * @}
   */

  /**
   * @name UI population
   *
   * @{
   */

  /**
   * Populate a UI element on behalf of the host.
   *
   * If the request is not supported, then an unset optional (`None` in
   * Python) should be returned.
   *
   * The nature of the UI to populate, how it should be populated, and
   * what communication channels should be set up with the host, is
   * determined by considering all the parameters.
   *
   * In particular, the UI-specific traits determine the kind of UI that
   * the host wants to present, and the access mode determines whether
   * that UI is for a read or publishing operation. The documentation of
   * the traits must be consulted to understand their meaning.
   *
   * Once the kind of UI is determined, the data used to initialise it
   * (e.g. the target entities) can be extracted from the request
   * object.
   *
   * The request object may also provide a host or UI framework-specific
   * native data object that should be used as part of, or to contain,
   * any newly constructed UI. The UI-specific traits, combined with the
   * host's own documentation, determine how such native data should
   * be used.
   *
   * Finally, the request object may contain a callback for notifying
   * the host of updates to the state of the UI (e.g. through user
   * interaction).
   *
   * The initial returned state from this method should contain the
   * initially selected/populated entities and/or trait data, if any.
   *
   * The returned state may also contain a native data object - again,
   * how this should be used is determined by the UI traits and
   * host-specific documentation.
   *
   * Finally, the returned state may contain a callback allowing the
   * host to update the initial request with changes, e.g. the target
   * selection of entities.
   *
   * @param uiTraitsData UI-specific @ref trait "traits" (and their
   * associated properties, if any) determining the kind of UI to
   * create.
   *
   * @param uiAccess The host's intended usage of the output from the
   * UI element.
   *
   * @param uiRequest The request object containing UI-specific
   * parameters, as well as a callback hook for communicating
   * asynchronous UI state changes.
   *
   * @param context The calling context.
   *
   * @param hostSession The API session.
   *
   * @return Empty optional if this request is not supported (`None` in
   * Python), otherwise the initial state of the UI.
   */
  virtual std::optional<UIDelegateStateInterfacePtr> populateUI(
      const trait::TraitsDataConstPtr& uiTraitsData, access::UIAccess uiAccess,
      UIDelegateRequestPtr uiRequest, const ContextConstPtr& context,
      const HostSessionPtr& hostSession);

  /**
   * @}
   */
};
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
