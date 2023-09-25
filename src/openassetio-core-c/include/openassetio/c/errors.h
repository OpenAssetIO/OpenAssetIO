// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/errors/errorCodes.h>

#include "./namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * @defgroup oa_ErrorCode oa_ErrorCode
 *
 * C API error codes.
 *
 * @{
 */

/**
 * @defgroup oa_ErrorCode_aliases Aliases
 *
 * @{
 */
#define oa_ErrorCode_kOK OPENASSETIO_NS(ErrorCode_kOK)
#define oa_ErrorCode_kUnknown OPENASSETIO_NS(ErrorCode_kUnknown)
#define oa_ErrorCode_kException OPENASSETIO_NS(ErrorCode_kException)
#define oa_ErrorCode_kBadVariantAccess OPENASSETIO_NS(ErrorCode_kBadVariantAccess)
#define oa_ErrorCode_kOutOfRange OPENASSETIO_NS(ErrorCode_kOutOfRange)
#define oa_ErrorCode_kLengthError OPENASSETIO_NS(ErrorCode_kLengthError)
#define oa_ErrorCode OPENASSETIO_NS(ErrorCode)

/// @}
// oa_ErrorCode_aliases

// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  /// Error code indicating an OK result from a C API function.
  oa_ErrorCode_kOK = 0,
  /// Error code representing a generic non-exception type thrown.
  oa_ErrorCode_kUnknown = OPENASSETIO_ErrorCode_BEGIN,
  /// Error code representing a generic C++ exception.
  oa_ErrorCode_kException,
  /// Error code representing a C++ std::bad_variant_access exception.
  oa_ErrorCode_kBadVariantAccess,
  /// Error code representing a C++ std::out_of_range exception.
  oa_ErrorCode_kOutOfRange,
  /// Error code representing a C++ std::length_error exception.
  oa_ErrorCode_kLengthError
} oa_ErrorCode;

/// @}
// oa_ErrorCode
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
