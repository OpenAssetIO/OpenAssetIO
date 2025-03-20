// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd

#pragma once

#include <functional>
#include <optional>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

OPENASSETIO_DECLARE_PTR(UIDelegateInterface)

/**
 */
class OPENASSETIO_UI_EXPORT UIDelegateInterface {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateInterface)

  UIDelegateInterface();

  // TODO(DF): Fill out details

  /**
   * Polymorphic destructor.
   */
  virtual ~UIDelegateInterface() = default;

  /**
   * Returns an identifier to uniquely identify a specific UI delegate.
   *
   * This must match the identifier of the corresponding @ref
   * glossary_manager_plugin.
   *
   * @return Unique identifier of the UI delegate.
   *
   * @see @fqref{managerApi.ManagerInterface.identifier}
   * "ManagerInterface.identifier".
   */
  [[nodiscard]] virtual Str identifier() const = 0;

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
   * @return Map of info string key to primitive value.
   */
  [[nodiscard]] virtual InfoDictionary info();
};
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
