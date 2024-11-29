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
 * @defgroup oa_managerApi_SharedHostSession oa_managerApi_SharedHostSession
 *
 * C API for the \fqref{managerApi.HostSession}
 * "managerApi::HostSession C++ type".
 *
 * @{
 */

/**
 * @defgroup oa_managerApi_SharedHostSession_aliases Aliases
 *
 * @{
 */
#define oa_managerApi_SharedHostSession_t OPENASSETIO_NS(managerApi_SharedHostSession_t)
#define oa_managerApi_SharedHostSession_h OPENASSETIO_NS(managerApi_SharedHostSession_h)

/// @}
// oa_managerApi_SharedHostSession_aliases

/**
 * Opaque handle type representing a @fqref{managerApi.HostSession}
 * "HostSession" instance.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_managerApi_SharedHostSession_t* oa_managerApi_SharedHostSession_h;

/// @}
// oa_managerApi_SharedHostSession
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
