// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>  // For OPENASSETIO_VERSION

/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * Prefix `openassetio_vX_Y_` to a given symbol name, where `X_Y` is
 * the current API version.
 *
 * @hideinitializer
 */
#define OPENASSETIO_NS(symbol) OPENASSETIO_NS_WITH_VER(OPENASSETIO_VERSION, symbol)

/**
 * @}
 */

/**
 *  @private Utility to work around token pasting macro expansion rules.
 *
 *  Macros are not expanded when using the token pasing operator `##`.
 *  So we need two utility functions, the first expands the value of
 *  `OPENASSETIO_VERSION` passed from `OPENASSETIO_NS` as a `ver`
 *  parameter and passes that to the second macro, which does the final
 *  token pasting.
 *
 *  @{
 */
#define OPENASSETIO_NS_WITH_VER(ver, symbol) OPENASSETIO_NS_WITH_VER_IMPL(ver, symbol)
#define OPENASSETIO_NS_WITH_VER_IMPL(ver, symbol) openassetio_##ver##_##symbol
/**
 * @}
 */
