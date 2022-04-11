// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include "../SimpleString.h"
#include "../namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * Opaque handle type representing a
 * @fqref{managerAPI::ManagerInterface} "ManagerInterface" instance.
 *
 * A `managerAPI_ManagerInterface_h` is provided by a @ref manager C
 * plugin and henceforth passed verbatim into C API functions that
 * expect a `ManagerInterface` handle.
 *
 * In particular, the associated @fqcref{managerAPI_ManagerInterface_s}
 * "ManagerInterface suite" of C function pointers, also provided by the
 * manager plugin, requires an opaque handle to be passed in all
 * function signatures, simulating the `this` pointer of a C++ class.
 *
 * The handle is not parsed directly within OpenAssetIO, so can
 * technically point to any data the manager plugin wishes.
 *
 * @see @fqcref{managerAPI_ManagerInterface_s}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct OPENASSETIO_NS(managerAPI_ManagerInterface_t) *
    OPENASSETIO_NS(managerAPI_ManagerInterface_h);

/**
 * Function pointer suite for a @fqref{managerAPI::ManagerInterface}
 * "ManagerInterface" C API.
 *
 * Instances of this suite are provided by a @ref manager C plugin.
 *
 * The function pointers correspond to member functions of the
 * @fqref{managerAPI::ManagerInterface} "ManagerInterface" C++ class,
 * and are expected to provide the same functionality but as a
 * C-friendly API.
 *
 * @see @fqcref{managerAPI_ManagerInterface_h}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /**
   * Destructor function.
   *
   * This will be called if/when OpenAssetIO is done with a
   * @fqcref{managerAPI_ManagerInterface_h}
   * "managerAPI_ManagerInterface_h" handle and will not attempt to use
   * it again.
   *
   * Any cleanup associated with the provided handle should be executed
   * in the implementation of this function.
   *
   * @param handle Opaque handle representing a `ManagerInterface`
   * instance.
   */
  void (*dtor)(OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle);

  /**
   * C equivalent of the
   * @fqref{managerAPI::ManagerInterface::identifier} "identifier"
   * member function.
   *
   * @param[out] err Storage for error message, if any.
   * @param[out] out Storage for the identifier string, if no error
   * occurred. @param handle Opaque handle representing
   * `ManagerInterface` instance.
   * @return @fqcref{kOK} "kOK" if no error occurred, an error code
   * otherwise.
   */
  int (*identifier)(OPENASSETIO_NS(SimpleString) * err, OPENASSETIO_NS(SimpleString) * out,
                    OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle);

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
   * @return @fqcref{kOK} "kOK" if no error occurred, an error code
   * otherwise.
   */
  int (*displayName)(OPENASSETIO_NS(SimpleString) * err, OPENASSETIO_NS(SimpleString) * out,
                     OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle);
} OPENASSETIO_NS(managerAPI_ManagerInterface_s);

/**
 * @}
 */
#ifdef __cplusplus
}
#endif
