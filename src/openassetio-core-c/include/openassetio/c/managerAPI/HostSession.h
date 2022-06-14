// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include "../namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * @defgroup oa_managerAPI_SharedHostSession oa_managerAPI_SharedHostSession
 *
 * C API for the \fqref{managerAPI::HostSession}
 * "managerAPI::HostSession C++ type".
 *
 * @{
 */

/**
 * @defgroup oa_managerAPI_SharedHostSession_aliases Aliases
 *
 * @{
 */
#define oa_managerAPI_SharedHostSession_t OPENASSETIO_NS(managerAPI_SharedHostSession_t)
#define oa_managerAPI_SharedHostSession_h OPENASSETIO_NS(managerAPI_SharedHostSession_h)

/// @todo HostSession method bindings

/// @}
// oa_managerAPI_SharedHostSession_aliases

/**
 * Opaque handle type representing a @fqref{managerAPI::HostSession}
 * "HostSession" instance.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_managerAPI_SharedHostSession_t* oa_managerAPI_SharedHostSession_h;

/// @}
// oa_managerAPI_SharedHostSession
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
