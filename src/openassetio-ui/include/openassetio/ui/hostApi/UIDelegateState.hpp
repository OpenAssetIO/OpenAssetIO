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
OPENASSETIO_FWD_DECLARE(ui::hostApi, UIDelegateRequestInterface)
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateStateInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

OPENASSETIO_DECLARE_PTR(UIDelegateState)

/**
 * Class encapsulating the @ref glossary_UI_Delegate state that may
 * change over time.
 *
 * The UI Delegate provides instances of this class to a host upon @ref
 * UIDelegate.populateUI "initiating a request" for UI delegation, and
 * when @ref UIDelegateRequestInterface.stateChangedCallback
 * "notifying of UI state changes".
 *
 * As well as providing the initial/updated UI state, this class also
 * holds a callback that can be used to update the parameters of the
 * associated ongoing @ref UIDelegateRequestInterface "request".
 */
class OPENASSETIO_UI_EXPORT UIDelegateState {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateState)
  /// Callback type for the host to notify the UI delegate of changes
  /// to the initial request.
  using UpdateRequestCallback = std::function<void(std::optional<UIDelegateRequestInterfacePtr>)>;

  /**
   * Constructs a new UIDelegateState wrapping a @ref manager UI
   * delegate's implementation.
   *
   * @note Instances of this class should not be constructed directly by
   * the host.
   *
   * @param uiDelegateStateInterface Implementation of the underlying
   * state.
   *
   * @return Newly created instance wrapped in a `std::shared_ptr`.
   */
  static Ptr make(managerApi::UIDelegateStateInterfacePtr uiDelegateStateInterface);

  /**
   * Arbitrary data object included with the state.
   *
   * It is up to the host to document what should be placed in here, if
   * anything.
   *
   * For example, it could be the top-level widget created by the UI
   * delegate, ready to be inserted into the UI hierarchy by the host.
   *
   * Note that for Python hosts, this must return a CPython `PyObject*`.
   */
  [[nodiscard]] std::any nativeData();

  /**
   * List of entity references considered relevant to the host by the
   * UI delegate.
   *
   * For example, this could be the entities chosen by the user in a
   * browser.
   */
  [[nodiscard]] EntityReferences entityReferences();

  /**
   * List of traits and their properties considered relevant to the
   * host by the UI delegate.
   *
   * For example, this could include additional data to be published,
   * which the host may or may not wish to further process.
   */
  [[nodiscard]] trait::TraitsDatas entityTraitsDatas();

  /**
   * Callback to be called by the host to notify the UI delegate that
   * the request has changed.
   *
   * For example, if the current selection has changed.
   *
   * If the host calls the callback with an empty optional (`None` in
   * Python), this notifies the UI delegate that the request is finished
   * (e.g. the UI element is about to be destroyed) and any dangling
   * state should be cleaned up. See also @ref UIDelegate.close.
   */
  [[nodiscard]] std::optional<UpdateRequestCallback> updateRequestCallback();

  ~UIDelegateState() = default;
  UIDelegateState(const UIDelegateState &other) = delete;
  UIDelegateState(UIDelegateState &&other) noexcept = default;
  UIDelegateState &operator=(const UIDelegateState &other) = delete;
  UIDelegateState &operator=(UIDelegateState &&other) noexcept = default;

 private:
  explicit UIDelegateState(managerApi::UIDelegateStateInterfacePtr uiDelegateStateInterface);
  managerApi::UIDelegateStateInterfacePtr uiDelegateStateInterface_;
};

}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
