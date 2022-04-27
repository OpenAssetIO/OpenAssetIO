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

// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  /// Error code indicating an OK result from a C API function.
  OPENASSETIO_NS(ErrorCode_kOK) = 0,
  /// Error code representing a generic C++ exception.
  OPENASSETIO_NS(ErrorCode_kUnknown),
  /// Error code representing a C++ std::bad_variant_access exception.
  OPENASSETIO_NS(ErrorCode_kBadVariantAccess),
  /// Error code representing a C++ std::out_of_range exception.
  OPENASSETIO_NS(ErrorCode_kOutOfRange),
  /// Error code representing a C++ std::length_error exception.
  OPENASSETIO_NS(ErrorCode_kLengthError)
} OPENASSETIO_NS(ErrorCode);
/**
 * @}
 */
#ifdef __cplusplus
}
#endif
