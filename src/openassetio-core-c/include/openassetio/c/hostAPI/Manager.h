// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/export.h>

#include "../InfoDictionary.h"
#include "../StringView.h"
#include "../errors.h"
#include "../managerAPI/ManagerInterface.h"
#include "../namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 *
 * @{
 */

/**
 * Opaque handle type representing a \fqref{hostAPI::Manager} "Manager".
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct OPENASSETIO_NS(hostAPI_Manager_t) * OPENASSETIO_NS(hostAPI_Manager_h);

/**
 * Constructor function.
 *
 * Allocates a new \fqref{hostAPI::Manager} "Manager", which should be
 * deallocated by \fqcref{hostAPI_Manager_dtor} "dtor" when the
 * `Manager` is no longer in use.
 *
 * @param[out] err Storage for error message, if any.
 * @param[out] handle
 * @param managerInterfaceHandle  A handle to a
 * \fqref{managerAPI::ManagerInterface} that the `Manager` will delegate
 * to.
 */
OPENASSETIO_CORE_C_EXPORT OPENASSETIO_NS(ErrorCode)
    OPENASSETIO_NS(hostAPI_Manager_ctor)(OPENASSETIO_NS(StringView) * err,
                                         OPENASSETIO_NS(hostAPI_Manager_h) * handle,
                                         OPENASSETIO_NS(managerAPI_ManagerInterface_h)
                                             managerInterfaceHandle);

/**
 * Destructor function.
 *
 * Deallocates a \fqref{hostAPI::Manager} "Manager" that was previously
 * created using \fqcref{hostAPI_Manager_ctor}. The handle should not
 * be used after calling this function.
 */
OPENASSETIO_CORE_C_EXPORT void OPENASSETIO_NS(hostAPI_Manager_dtor)(
    OPENASSETIO_NS(hostAPI_Manager_h) handle);

/**
 * C equivalent of the
 * @fqref{hostAPI::Manager::identifier} "identifier"
 * member function.
 *
 * @param[out] err Storage for error message, if any.
 * @param[out] out Storage for the identifier string, if no error
 * occurred. @param handle Opaque handle representing
 * `ManagerInterface` instance.
 * @return @fqcref{ErrorCode_kOK} "kOK" if no error occurred, an
 * error code otherwise.
 */
OPENASSETIO_CORE_C_EXPORT OPENASSETIO_NS(ErrorCode)
    OPENASSETIO_NS(hostAPI_Manager_identifier)(OPENASSETIO_NS(StringView) * err,
                                               OPENASSETIO_NS(StringView) * out,
                                               OPENASSETIO_NS(hostAPI_Manager_h) handle);

/**
 * C equivalent of the
 * @fqref{hostAPI::Manager::displayName} "displayName"
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
OPENASSETIO_CORE_C_EXPORT OPENASSETIO_NS(ErrorCode)
    OPENASSETIO_NS(hostAPI_Manager_displayName)(OPENASSETIO_NS(StringView) * err,
                                                OPENASSETIO_NS(StringView) * out,
                                                OPENASSETIO_NS(hostAPI_Manager_h) handle);

/**
 * C equivalent of the
 * @fqref{hostAPI::Manager::info} "info"
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
OPENASSETIO_CORE_C_EXPORT OPENASSETIO_NS(ErrorCode)
    OPENASSETIO_NS(hostAPI_Manager_info)(OPENASSETIO_NS(StringView) * err,
                                         OPENASSETIO_NS(InfoDictionary_h) out,
                                         OPENASSETIO_NS(hostAPI_Manager_h) handle);

/**
 * @}
 */
#ifdef __cplusplus
}
#endif
