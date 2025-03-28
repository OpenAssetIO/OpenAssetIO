// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#pragma once

#include <any>
#include <functional>
#include <memory>
#include <optional>
#include <string>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/access.hpp>

OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateInterface)
OPENASSETIO_FWD_DECLARE(ui::hostApi, UIDelegateRequestInterface)
OPENASSETIO_FWD_DECLARE(ui::hostApi, UIDelegateState)
OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(Context)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to anyone wanting to add support
 for a host application.

 If you are an asset management system developer, see @ref managerApi.
*/
namespace ui::hostApi {

OPENASSETIO_DECLARE_PTR(UIDelegate)

/**
 * The UIDelegate is the @ref host facing representation of an @ref
 * asset_management_system "asset management system's" bespoke @ref
 * glossary_UI_Delegate.
 *
 * UIDelegate instances shouldn't be directly constructed by the host.
 * An instance of the class for any given asset management system can be
 * retrieved from a @fqref{ui.hostApi.UIDelegateFactory}
 * "UIDelegateFactory", using the
 * @fqref{ui.hostApi.UIDelegateFactory.createUIDelegate}
 * "UIDelegateFactory.createUIDelegate()" method with an appropriate
 * manager @ref identifier.
 *
 * @code
 * factory = openassetio.ui.hostApi.UIDelegateFactory(
 *     hostImpl, consoleLogger, pluginFactory)
 * uiDelegate = factory.createUIDelegate("org.openassetio.test.manager")
 * @endcode
 *
 * A UIDelegate instance is the interaction point for augmenting or
 * replacing UI elements with those provided by an asset management
 * system. It provides methods to uniquely identify the underlying
 * implementation, and to populate UI elements in a framework-agnostic
 * manner.
 *
 * The UIDelegate API should not be considered thread-safe.
 */
class OPENASSETIO_UI_EXPORT UIDelegate final {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegate)

  /**
   * Constructs a new UIDelegate wrapping the supplied UI delegate
   * interface and host session.
   */
  [[nodiscard]] static UIDelegatePtr make(managerApi::UIDelegateInterfacePtr uiDelegateInterface,
                                          openassetio::managerApi::HostSessionPtr hostSession);

  /**
   * Destructor that will call @ref close() wrapped in a try-catch.
   */
  ~UIDelegate();

  /**
   * @name  UI Delegate Identification
   *
   * These functions provide general identity information about UI
   * delegate itself. These can all be called before @ref initialize has
   * been called.
   *
   * @{
   */

  /**
   * Returns an identifier to uniquely identify the UI delegate.
   *
   * This identifier is used with the @ref UIDelegateFactory
   * to select which UI delegate to initialize, and
   * so can be used in preferences etc to persist the chosen UI delegate.
   *
   * The identifier will use only alpha-numeric characters and '.', '_'
   * or '-'. They generally follow the 'reverse-DNS' style, for example:
   *
   *     "org.openassetio.test.manager"
   */
  [[nodiscard]] Identifier identifier() const;

  /**
   * Returns a human readable name to be used to reference this
   * specific asset manager in user-facing displays.
   * For example:
   *
   *     "OpenAssetIO Test UI Delegate"
   */
  [[nodiscard]] Str displayName() const;

  /**
   * Returns other information that may be useful about this UI
   * delegate. This can contain arbitrary key/value pairs.
   *
   * The @ref constants.kInfoKey_IsPython constant is used to signal to
   * the that the UI delegate is written in Python, and therefore any
   * @ref UIDelegateRequestInterface.nativeData and @ref
   * UIDelegateState.nativeData will/must be a CPython `PyObject*`.
   *
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] InfoDictionary info();

  /**
   * @}
   */

  /**
   * @name Initialization
   *
   * @{
   */

  /**
   * Retrieve settings currently applied to this UI delegate.
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
   * Prepares the UI delegate for interaction with a host.
   *
   * In order to provide light weight inspection of available
   * UI delegates, initial construction must be cheap. However most
   * systems require some kind of handshake or back-end setup in order
   * to make entity-related queries. As such, the @ref initialize method
   * is the instruction to the UI delegate to prepare itself for full
   * interaction.
   *
   * If an exception is raised by this call, it's is safe to assume
   * that a fatal error occurred, and this UI delegate is not available,
   * and should be retried later.
   *
   * If no exception is raised, it can be assumed that the UI delegate
   * is ready. It is the implementation's responsibility to deal with
   * transient connection errors (if applicable) once initialized.
   *
   * The behavior of calling initialize() on an already initialized
   * UI delegate is to re-initialize the UI delegate with any updated
   * settings that are provided. If an error was raised previously, then
   * initialization will be re-attempted.
   *
   * @note This must be called prior to any UI-related calls or
   * an exception will be raised.
   *
   * @note This method may block for extended periods of time.
   *
   * @param uiDelegateSettings Settings to apply to the UI delegate on
   * initialisation.
   */
  void initialize(InfoDictionary uiDelegateSettings);

  /**
   * Instruct the UI delegate to dispose of all active references to
   * delegated UI.
   *
   * Called automatically on destruction of this UIDelegate instance,
   * but can be called independently in order to reuse this instance.
   *
   * This should be used when all UI elements created by the UI delegate
   * are being destroyed wholesale. The UI delegate will consider any
   * handles to UI elements as unsafe when this method is called.
   *
   * To close a single UI delegation request, call the associated @ref
   * UIDelegateState.updateRequestCallback with an unset request (`None`
   * in Python), if available.
   *
   * @warning When this is called during destruction of a Python
   * instance, the Python GIL will be held for the duration of the call.
   */
  void close();

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
   * indicates that UI delegation requests of this kind are not
   * supported, @ref populateUI calls will be refused for these
   * arguments.
   *
   * This method may be called early on to determine whether to attempt
   * to present OpenAssetIO related UI elements to the user, and to
   * retrieve other sundry UI related metadata that is not specific to
   * an individual request.
   *
   * Note that even if this method returns positively, @ref populateUI
   * may still refuse to provide a UI element, based on the specific
   * request at the time.
   *
   * Consult the relevant traits library to discover the available UI
   * policy-specific traits. For example, the <a
   * href="https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation"
   * target="_blank">OpenAssetIO-MediaCreation</a> project provides
   * traits related to computer graphics and media production. In
   * particular, if the return value is imbued with the `Managed` UI
   * policy trait from the MediaCreation library, then UI delegation
   * requests are likely to succeed.
   *
   * As well as determining whether a request is likely to be supported,
   * additional metadata that may be used by the host can be populated
   * in the returned @ref trait.TraitsData "TraitsData". For example,
   * this could include a "display name" that the host may use in the
   * titles of tabs or windows that contain the delegated UI element(s).
   *
   * This method is opt-in - it is safe to skip this and call @ref
   * populateUI and deal with the response. However, constructing the
   * arguments for @ref populateUI may be an expensive operation, only
   * for it to be unsupported. Also, this method may provide additional
   * metadata useful in optimising the user experience.
   *
   * @param uiTraitSet The set of UI-specific @ref trait "traits"
   * determining the kind of UI element the host may wish to delegate.
   *
   * @param uiAccess Type of operation that the delegated UI will be
   * used for.
   *
   * @param context The calling context.
   *
   * @return Policy-specific traits with their associated properties
   * filled, if applicable.
   */
  virtual trait::TraitsDataPtr uiPolicy(const trait::TraitSet& uiTraitSet,
                                        access::UIAccess uiAccess, const ContextConstPtr& context);

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
   * Python) will be returned.
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
   * (e.g. the target entities) should be placed in the request object.
   *
   * The request object may also provide a host or UI framework-specific
   * native data object that should be used as part of, or to contain,
   * any newly constructed UI. The UI-specific traits, combined with the
   * host's own documentation, determine how such native data should
   * be used.
   *
   * Finally, the request object may contain a callback for notifying
   * the host of updates to the state of the UI (e.g. due to user
   * interaction).
   *
   * The initial returned state from this method will contain the
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
   * @param uiRequestInterface The request object containing UI-specific
   * parameters, as well as a callback hook for communicating
   * asynchronous UI state changes.
   *
   * @param context The calling context.
   *
   * @return Empty optional (`None` in Python) if this request is not
   * supported, otherwise the initial state of the UI.
   */
  std::optional<UIDelegateStatePtr> populateUI(const trait::TraitsDataConstPtr& uiTraitsData,
                                               access::UIAccess uiAccess,
                                               UIDelegateRequestInterfacePtr uiRequestInterface,
                                               const ContextConstPtr& context);

  /**
   * @}
   */

  UIDelegate(const UIDelegate& other) = delete;
  UIDelegate(UIDelegate&& other) noexcept = default;
  UIDelegate& operator=(const UIDelegate& other) = delete;
  UIDelegate& operator=(UIDelegate&& other) noexcept = default;

 private:
  explicit UIDelegate(managerApi::UIDelegateInterfacePtr uiDelegateInterface,
                      openassetio::managerApi::HostSessionPtr hostSession);

  managerApi::UIDelegateInterfacePtr uiDelegateInterface_;
  openassetio::managerApi::HostSessionPtr hostSession_;
};
}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
