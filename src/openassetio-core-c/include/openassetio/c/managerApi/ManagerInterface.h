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
 * @defgroup oa_managerApi_SharedManagerInterface oa_managerApi_SharedManagerInterface
 *
 * C API for the \fqref{managerApi.ManagerInterface}
 * "managerApi::ManagerInterface C++ type".
 *
 * @{
 */

/**
 * @defgroup oa_managerApi_SharedManagerInterface_aliases Aliases
 *
 * @{
 */
#define oa_managerApi_SharedManagerInterface_t OPENASSETIO_NS(managerApi_SharedManagerInterface_t)
#define oa_managerApi_SharedManagerInterface_h OPENASSETIO_NS(managerApi_SharedManagerInterface_h)

/// @}
// oa_managerApi_SharedManagerInterface_aliases

/**
 * Opaque handle type representing a @fqref{managerApi.ManagerInterface}
 * "ManagerInterface" instance.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_managerApi_SharedManagerInterface_t* oa_managerApi_SharedManagerInterface_h;

/// @}
// oa_managerApi_SharedManagerInterface
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
