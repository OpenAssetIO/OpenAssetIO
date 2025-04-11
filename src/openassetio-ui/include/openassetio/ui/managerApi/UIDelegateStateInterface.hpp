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
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateRequest)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

OPENASSETIO_DECLARE_PTR(UIDelegateStateInterface)

/**
 * Abstract interface encapsulating the @ref glossary_UI_Delegate state
 * that may change over time.
 *
 * The UI Delegate is expected to subclass this class and implement its
 * methods. Instances are then be provided to a @ref host upon @ref
 * UIDelegateInterface.populateUI "initiating a request" for UI
 * delegation, and when @ref UIDelegateRequest.stateChangedCallback
 * "notifying the host of UI state changes".
 *
 * This class also holds a callback, which the host can use to update
 * the parameters of the ongoing @ref UIDelegateRequest "request".
 */
class OPENASSETIO_UI_EXPORT UIDelegateStateInterface {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateStateInterface)
  /// Callback type for the host to notify the UI delegate of changes to
  /// the initial request.
  using UpdateRequestCallback = std::function<void(std::optional<UIDelegateRequestPtr>)>;

  /// Defaulted destructor.
  virtual ~UIDelegateStateInterface() = default;

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
  [[nodiscard]] virtual std::any nativeData();

  /**
   * List of entity references considered relevant to the host by the
   * UI delegate.
   *
   * For example, this could be the entities chosen by the user in a
   * browser.
   */
  [[nodiscard]] virtual EntityReferences entityReferences();

  /**
   * List of traits and their properties considered relevant to the
   * host by the UI delegate.
   *
   * For example, this could include additional data to be published,
   * which the host may or may not wish to further process.
   */
  [[nodiscard]] virtual trait::TraitsDatas entityTraitsDatas();

  /**
   * Callback to be called by the host to notify the UI delegate that
   * the request has changed.
   *
   * For example, if the current selection has changed.
   *
   * If the host calls the callback with an empty optional (`None` in
   * Python), this notifies the UI delegate that the request is finished
   * (e.g. the UI element is about to be destroyed) and any dangling
   * state should be cleaned up. See also @ref
   * UIDelegateInterface.close.
   *
   * @note The request provided to the callback is a reference type,
   * i.e. it may be the same underlying instance as a previous request,
   * so checking equality of successive requests is insufficient when
   * computing changes. Instead, extract the relevant elements of a
   * request early (e.g. @ref UIDelegateRequest.entityReferences()) to
   * use for subsequent comparisons.
   */
  [[nodiscard]] virtual std::optional<UpdateRequestCallback> updateRequestCallback();
};

}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
