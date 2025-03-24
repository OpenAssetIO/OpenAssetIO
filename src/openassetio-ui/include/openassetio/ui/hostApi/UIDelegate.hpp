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

OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateInterface)
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
 * asset_management_system "asset management system's" bespoke UI.
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
   * @}
   */

  ~UIDelegate() = default;
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
