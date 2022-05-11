// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include "../InfoDictionary.h"
#include "../StringView.h"
#include "../errors.h"
#include "../namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * Opaque handle type provided by @ref manager plugins that provide
 * their @fqref{managerAPI::ManagerInterface} "ManagerInterface"
 * implementation via the C API plugin system.
 *
 * The associated @fqcref{managerAPI_CManagerInterface_s}
 * "ManagerInterface suite" of C function pointers, also provided by the
 * manager plugin, requires this opaque handle to be passed in all
 * function signatures, simulating the `this` pointer of a C++ method.
 *
 * The handle is not parsed directly within OpenAssetIO, so can
 * technically point to any data the manager plugin wishes.
 *
 * @see @fqcref{managerAPI_CManagerInterface_s}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct OPENASSETIO_NS(managerAPI_CManagerInterface_t) *
    OPENASSETIO_NS(managerAPI_CManagerInterface_h);

/**
 * Function pointer suite provided by @ref manager plugins that provide
 * the @fqref{managerAPI::ManagerInterface} "ManagerInterface"
 * implementation via the C API plugin system.
 *
 * Instances of this suite are provided by a @ref manager C plugin.
 *
 * The function pointers correspond to member functions of the
 * @fqref{managerAPI::ManagerInterface} "ManagerInterface" C++ class,
 * and are expected to provide the same functionality but as a
 * C-friendly API.
 *
 * @see @fqcref{managerAPI_CManagerInterface_h}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /**
   * Destructor function.
   *
   * This will be called if/when OpenAssetIO is done with a
   * @fqcref{managerAPI_CManagerInterface_h}
   * "managerAPI_CManagerInterface_h" handle and will not attempt to use
   * it again.
   *
   * Any cleanup associated with the provided handle should be executed
   * in the implementation of this function.
   *
   * @param handle Opaque handle representing a `ManagerInterface`
   * instance.
   */
  void (*dtor)(OPENASSETIO_NS(managerAPI_CManagerInterface_h) handle);

  /**
   * C equivalent of the
   * @fqref{managerAPI::ManagerInterface::identifier} "identifier"
   * member function.
   *
   * @param[out] err Storage for error message, if any.
   * @param[out] out Storage for the identifier string, if no error
   * occurred. @param handle Opaque handle representing
   * `ManagerInterface` instance.
   * @return @fqcref{ErrorCode_kOK} "kOK" if no error occurred, an
   * error code otherwise.
   */
  OPENASSETIO_NS(ErrorCode)
  (*identifier)(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
                OPENASSETIO_NS(managerAPI_CManagerInterface_h) handle);

  /**
   * C equivalent of the
   * @fqref{managerAPI::ManagerInterface::displayName} "displayName"
   * member function.
   *
   * @param[out] err Storage for error message, if any.
   * @param[out] out Storage for the display name string, if no error
   * occurred.
   * @param handle Opaque handle representing `ManagerInterface`
   * instance.
   * @return @fqcref{ErrorCode_kOK} "kOK" if no error occurred, an
   * error code otherwise.
   */
  OPENASSETIO_NS(ErrorCode)
  (*displayName)(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
                 OPENASSETIO_NS(managerAPI_CManagerInterface_h) handle);

  /**
   * C equivalent of the
   * @fqref{managerAPI::ManagerInterface::info} "info"
   * member function.
   *
   * @param[out] err Storage for error message, if any.
   * @param[out] out Handle to pre-existing dictionary that should be
   * populated with entries.
   * @param handle Opaque handle representing `ManagerInterface`
   * instance.
   * @return @fqcref{ErrorCode_kOK} "kOK" if no error occurred, an
   * error code otherwise.
   */
  OPENASSETIO_NS(ErrorCode)
  (*info)(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) out,
          OPENASSETIO_NS(managerAPI_CManagerInterface_h) handle);
} OPENASSETIO_NS(managerAPI_CManagerInterface_s);

/**
 * @}
 */
#ifdef __cplusplus
}
#endif
