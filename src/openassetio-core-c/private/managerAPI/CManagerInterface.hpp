// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/export.h>
#include <openassetio/export.h>

#include <openassetio/c/managerAPI/ManagerInterface.h>
#include <openassetio/managerAPI/ManagerInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace managerAPI {

/**
 * ManagerInterface implementation wrapping a manager plugin defined via
 * the C API.
 */
class OPENASSETIO_CORE_C_EXPORT CManagerInterface : ManagerInterface {
 public:
  /**
   * Construct from a provided opaque handle and C function pointer
   * suite.
   *
   * @param handle Opaque handle to pass to suite functions.
   * @param suite Function pointer suite to call from within member
   * functions.
   */
  CManagerInterface(OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle,
                    OPENASSETIO_NS(managerAPI_ManagerInterface_s) suite);

  /// Destructor that calls the C suite's `dtor` function.
  ~CManagerInterface() override;

  /// Wrap the C suite's `identifier` function.
  [[nodiscard]] Str identifier() const override;

  /// Wrap the C suite's `displayName` function.
  [[nodiscard]] Str displayName() const override;

 private:
  /// Opaque handle representing a ManagerInterface for the C API.
  OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle_;
  /// Suite of C API function pointers to delegate calls to.
  OPENASSETIO_NS(managerAPI_ManagerInterface_s) suite_;
};

}  // namespace managerAPI
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
