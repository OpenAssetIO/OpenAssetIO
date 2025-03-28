// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <any>
#include <functional>
#include <optional>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(TraitsData)
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateStateInterface)
OPENASSETIO_FWD_DECLARE(ui::hostApi, UIDelegateRequestInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

OPENASSETIO_DECLARE_PTR(UIDelegateRequest)

/**
 * Class encapsulating a @ref glossary_UI_Delegate request that may
 * change over time.
 *
 * The @ref host provides instances of this class to a UI delegate when
 * @ref UIDelegateInterface.populateUI "initiating a request" for UI
 * delegation, and when @ref
 * UIDelegateStateInterface.updateRequestCallback
 * "updating an ongoing request".
 *
 * As well as providing information for initialising/updating a
 * specific request, this class also holds a callback that should be
 * used to notify the host of relevant updates to the UI delegate's
 * internal @ref UIDelegateStateInterface "state".
 */
class OPENASSETIO_UI_EXPORT UIDelegateRequest final {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateRequest)
  /// Callback type for the UI delegate to notify the host of state
  /// changes.
  using StateChangedCallback = std::function<void(UIDelegateStateInterfacePtr)>;

  /**
   * Constructs a new UIDelegateRequest wrapping a @ref host
   * implementation.
   *
   * @note Instances of this class should not be constructed directly by
   * the host.
   *
   * @param uiDelegateRequestInterface Implementation of the underlying
   * request.
   *
   * @return Newly created instance wrapped in a `std::shared_ptr`.
   */
  static Ptr make(hostApi::UIDelegateRequestInterfacePtr uiDelegateRequestInterface);

  /**
   * Arbitrary data object included with the request.
   *
   * It is up to the host to document what will be placed in here, if
   * anything.
   *
   * For example, it could be a container widget to be populated
   * by the UI delegate.
   *
   * Note that for Python UI delegates, this must contain a CPython
   * `PyObject*`.
   */
  [[nodiscard]] std::any nativeData();

  /**
   * List of entity references associated with the request.
   *
   * For example, this could be the "current selection", for which the
   * UI delegate is expected to provide actions or additional
   * information.
   */
  [[nodiscard]] EntityReferences entityReferences();

  /**
   * List of traits and their properties associated with the request.
   *
   * For example, this could be data that's intended to be published,
   * allowing the UI delegate a chance to augment or finesse the
   * published data.
   */
  [[nodiscard]] trait::TraitsDatas entityTraitsDatas();

  /**
   * Callback to be called by the UI delegate to notify the host of
   * state changes.
   *
   * For example, when the user selects an entity in a browser.
   */
  [[nodiscard]] std::optional<StateChangedCallback> stateChangedCallback();

  ~UIDelegateRequest() = default;
  UIDelegateRequest(const UIDelegateRequest& other) = delete;
  UIDelegateRequest(UIDelegateRequest&& other) noexcept = default;
  UIDelegateRequest& operator=(const UIDelegateRequest& other) = delete;
  UIDelegateRequest& operator=(UIDelegateRequest&& other) noexcept = default;

 private:
  explicit UIDelegateRequest(hostApi::UIDelegateRequestInterfacePtr uiDelegateRequestInterface);
  hostApi::UIDelegateRequestInterfacePtr uiDelegateRequestInterface_;
};
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
