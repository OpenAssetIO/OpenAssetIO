// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/export.h>

#include "../InfoDictionary.h"
#include "../StringView.h"
#include "../errors.h"
#include "../managerAPI/HostSession.h"
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
 * @defgroup oa_hostAPI_Manager oa_hostAPI_Manager
 *
 * C API for the \fqref{hostAPI::Manager} "hostAPI::Manager C++ type".
 *
 * @{
 */

/**
 * @defgroup oa_hostAPI_Manager_aliases Aliases
 *
 * @{
 */
#define oa_hostAPI_Manager_t OPENASSETIO_NS(hostAPI_Manager_t)
#define oa_hostAPI_Manager_h OPENASSETIO_NS(hostAPI_Manager_h)
#define oa_hostAPI_Manager_ctor OPENASSETIO_NS(hostAPI_Manager_ctor)
#define oa_hostAPI_Manager_h OPENASSETIO_NS(hostAPI_Manager_h)
#define oa_hostAPI_Manager_identifier OPENASSETIO_NS(hostAPI_Manager_identifier)
#define oa_hostAPI_Manager_displayName OPENASSETIO_NS(hostAPI_Manager_displayName)
#define oa_hostAPI_Manager_info OPENASSETIO_NS(hostAPI_Manager_info)

/// @}
// oa_hostAPI_Manager_aliases

/**
 * Opaque handle type representing a \fqref{hostAPI::Manager} "Manager".
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_hostAPI_Manager_t* oa_hostAPI_Manager_h;

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
 * @param hostSessionHandle  A handle to a
 * \fqref{managerAPI::HostSession} that the `Manager` will supply to the
 * held interface as required.
 * to.
 *
 **/
// TODO(DF): The ownership semantic of a
// `ManagerInterface`/`HostSession` handle is "shared" (i.e. it wraps a
// dynamically allocated `shared_ptr`), however there is no way to
// "release" a `ManagerInterface` handle. We need to figure out where
// these handles are created and what API we need around them - probably
// a `dtor`, at minimum. Or possibly `Manager`s in the C API should only
// be constructed via some factory, and there is no need for this `ctor`
// and thus no need for a `ManagerInterface_h` handle?
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode
oa_hostAPI_Manager_ctor(oa_StringView* err, oa_hostAPI_Manager_h* handle,
                        oa_managerAPI_SharedManagerInterface_h managerInterfaceHandle,
                        oa_managerAPI_SharedHostSession_h hostSessionHandle);

/**
 * Destructor function.
 *
 * Deallocates a \fqref{hostAPI::Manager} "Manager" that was previously
 * created using \fqcref{hostAPI_Manager_ctor}. The handle should not
 * be used after calling this function.
 */
OPENASSETIO_CORE_C_EXPORT void oa_hostAPI_Manager_dtor(oa_hostAPI_Manager_h handle);

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_hostAPI_Manager_identifier(oa_StringView* err,
                                                                     oa_StringView* out,
                                                                     oa_hostAPI_Manager_h handle);

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_hostAPI_Manager_displayName(oa_StringView* err,
                                                                      oa_StringView* out,
                                                                      oa_hostAPI_Manager_h handle);

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_hostAPI_Manager_info(oa_StringView* err,
                                                               oa_InfoDictionary_h out,
                                                               oa_hostAPI_Manager_h handle);

/// @}
// oa_hostAPI_Manager
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
