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
 * @defgroup oa_managerApi_CManagerInterface oa_managerApi_CManagerInterface
 *
 * C API that C plugins must implement to satisfy the
 * \fqref{managerApi.ManagerInterface} "ManagerInterface" contract.
 *
 * @{
 */

/**
 * @defgroup oa_managerApi_CManagerInterface_aliases Aliases
 *
 * @{
 */
#define oa_managerApi_CManagerInterface_t OPENASSETIO_NS(managerApi_CManagerInterface_t)
#define oa_managerApi_CManagerInterface_h OPENASSETIO_NS(managerApi_CManagerInterface_h)
#define oa_managerApi_CManagerInterface_s OPENASSETIO_NS(managerApi_CManagerInterface_s)

/// @}
// oa_managerApi_CManagerInterface_aliases

/**
 * Opaque handle type provided by @ref manager plugins that provide
 * their @fqref{managerApi.ManagerInterface} "ManagerInterface"
 * implementation via the C API plugin system.
 *
 * The associated @fqcref{managerApi_CManagerInterface_s}
 * "ManagerInterface suite" of C function pointers, also provided by the
 * manager plugin, requires this opaque handle to be passed in all
 * function signatures, simulating the `this` pointer of a C++ method.
 *
 * The handle is not parsed directly within OpenAssetIO, so can
 * technically point to any data the manager plugin wishes.
 *
 * @see @fqcref{managerApi_CManagerInterface_s}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_managerApi_CManagerInterface_t* oa_managerApi_CManagerInterface_h;

/**
 * Function pointer suite provided by @ref manager plugins that provide
 * the @fqref{managerApi.ManagerInterface} "ManagerInterface"
 * implementation via the C API plugin system.
 *
 * Instances of this suite are provided by a @ref manager C plugin.
 *
 * The function pointers correspond to member functions of the
 * @fqref{managerApi.ManagerInterface} "ManagerInterface" C++ class,
 * and are expected to provide the same functionality but as a
 * C-friendly API.
 *
 * @see @fqcref{managerApi_CManagerInterface_h}
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /**
   * Destructor function.
   *
   * This will be called if/when OpenAssetIO is done with a
   * @fqcref{managerApi_CManagerInterface_h}
   * "managerApi_CManagerInterface_h" handle and will not attempt to use
   * it again.
   *
   * Any cleanup associated with the provided handle should be executed
   * in the implementation of this function.
   *
   * @param handle Opaque handle representing a `ManagerInterface`
   * instance.
   */
  void (*dtor)(oa_managerApi_CManagerInterface_h handle);

  /**
   * C equivalent of the
   * @fqref{managerApi.ManagerInterface.identifier} "identifier"
   * member function.
   *
   * @param[out] err Storage for error message, if any.
   * @param[out] out Storage for the identifier string, if no error
   * occurred. @param handle Opaque handle representing
   * `ManagerInterface` instance.
   * @return @fqcref{ErrorCode_kOK} "kOK" if no error occurred, an
   * error code otherwise.
   */
  oa_ErrorCode (*identifier)(oa_StringView* err, oa_StringView* out,
                             oa_managerApi_CManagerInterface_h handle);

  /**
   * C equivalent of the
   * @fqref{managerApi.ManagerInterface.displayName} "displayName"
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
  oa_ErrorCode (*displayName)(oa_StringView* err, oa_StringView* out,
                              oa_managerApi_CManagerInterface_h handle);

  /**
   * C equivalent of the
   * @fqref{managerApi.ManagerInterface.info} "info"
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
  oa_ErrorCode (*info)(oa_StringView* err, oa_InfoDictionary_h out,
                       oa_managerApi_CManagerInterface_h handle);
} oa_managerApi_CManagerInterface_s;

/// @}
// oa_managerApi_CManagerInterface
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
