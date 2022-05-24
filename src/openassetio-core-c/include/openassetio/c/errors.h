// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include "./namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

// Symbol namespacing.
#define oa_ErrorCode_kOK OPENASSETIO_NS(ErrorCode_kOK)
#define oa_ErrorCode_kUnknown OPENASSETIO_NS(ErrorCode_kUnknown)
#define oa_ErrorCode_kException OPENASSETIO_NS(ErrorCode_kException)
#define oa_ErrorCode_kBadVariantAccess OPENASSETIO_NS(ErrorCode_kBadVariantAccess)
#define oa_ErrorCode_kOutOfRange OPENASSETIO_NS(ErrorCode_kOutOfRange)
#define oa_ErrorCode_kLengthError OPENASSETIO_NS(ErrorCode_kLengthError)
#define oa_ErrorCode OPENASSETIO_NS(ErrorCode)

// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  /// Error code indicating an OK result from a C API function.
  oa_ErrorCode_kOK = 0,
  /// Error code representing a generic non-exception type thrown.
  oa_ErrorCode_kUnknown,
  /// Error code representing a generic C++ exception.
  oa_ErrorCode_kException,
  /// Error code representing a C++ std::bad_variant_access exception.
  oa_ErrorCode_kBadVariantAccess,
  /// Error code representing a C++ std::out_of_range exception.
  oa_ErrorCode_kOutOfRange,
  /// Error code representing a C++ std::length_error exception.
  oa_ErrorCode_kLengthError
} oa_ErrorCode;
/**
 * @}
 */
#ifdef __cplusplus
}
#endif
