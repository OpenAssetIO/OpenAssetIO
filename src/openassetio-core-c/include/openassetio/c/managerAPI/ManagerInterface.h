// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
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
 * @defgroup oa_managerAPI_SharedManagerInterface oa_managerAPI_SharedManagerInterface
 *
 * C API for the \fqref{managerAPI::ManagerInterface}
 * "managerAPI::ManagerInterface C++ type".
 *
 * @{
 */

/**
 * @defgroup oa_managerAPI_SharedManagerInterface_aliases Aliases
 *
 * @{
 */
#define oa_managerAPI_SharedManagerInterface_t OPENASSETIO_NS(managerAPI_SharedManagerInterface_t)
#define oa_managerAPI_SharedManagerInterface_h OPENASSETIO_NS(managerAPI_SharedManagerInterface_h)

/// @}
// oa_managerAPI_SharedManagerInterface_aliases

/**
 * Opaque handle type representing a @fqref{managerAPI::ManagerInterface}
 * "ManagerInterface" instance.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_managerAPI_SharedManagerInterface_t* oa_managerAPI_SharedManagerInterface_h;

/// @}
// oa_managerAPI_SharedManagerInterface
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
