// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd

#pragma once

#include <functional>
#include <optional>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
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
};
}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
