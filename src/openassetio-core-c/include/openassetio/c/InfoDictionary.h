// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <cstddef>
#include <cstdint>

#include <openassetio/c/export.h>

#include "./StringView.h"
#include "./errors.h"
#include "./namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * Opaque handle type representing a @fqref{InfoDictionary} "InfoDictionary"
 * instance.
 *
 * The associated @fqcref{InfoDictionary_s} "InfoDictionary suite" functions
 * operate on this handle type.
 *
 * The ownership semantics of this handle are "owned by client", that
 * is, the caller of the C API is responsible for deallocating using
 * the suite's `dtor` function once the InfoDictionary is no longer in use.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct OPENASSETIO_NS(InfoDictionary_t) * OPENASSETIO_NS(InfoDictionary_h);

/**
 * Function pointer suite for a @fqref{InfoDictionary} "InfoDictionary" C API.
 *
 * Instances of this suite are provided by the `InfoDictionary_suite`
 * function and operate on a @fqcref{InfoDictionary_h} "InfoDictionary handle".
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /**
   * Constructor function.
   *
   * The caller is responsible for deallocating via `dtor`.
   *
   * @param[out] error Storage for error message, if any.
   * @param[out] out Opaque handle to InfoDictionary.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*ctor)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_h) * out);

  /**
   * Destructor function.
   *
   * This should be called by the owner of the handle when the handle is
   * no longer in use. The underlying object will be destroyed and its
   * memory freed.
   *
   * @param handle Opaque handle to InfoDictionary.
   */
  void (*dtor)(OPENASSETIO_NS(InfoDictionary_h) handle);

  /**
   * Retrieve a boolean value from the map.
   *
   * Missing values will result in a @fqcref{ErrorCode_kOutOfRange} error
   * code.
   *
   * Values with the wrong data type will result in a
   * @fqcref{ErrorCode_kBadVariantAccess} error code.
   *
   * @param[out] error Storage for error message, if any.
   * @param[out] out Storage for retrieved value.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to query.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*getBool)(OPENASSETIO_NS(StringView) * error, bool* out,
             OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key);

  /**
   * Retrieve an integer value from the map.
   *
   * Missing values will result in a @fqcref{ErrorCode_kOutOfRange} error
   * code.
   *
   * Values with the wrong data type will result in a
   * @fqcref{ErrorCode_kBadVariantAccess} error code.
   *
   * @param[out] error Storage for error message, if any.
   * @param[out] out Storage for retrieved value.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to query.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*getInt)(OPENASSETIO_NS(StringView) * error, int64_t* out,
            OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key);

  /**
   * Retrieve a floating point value from the map.
   *
   * Missing values will result in a @fqcref{ErrorCode_kOutOfRange} error
   * code.
   *
   * Values with the wrong data type will result in a
   * @fqcref{ErrorCode_kBadVariantAccess} error code.
   *
   * @param[out] error Storage for error message, if any
   * @param[out] out Storage for retrieved value.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to query.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*getFloat)(OPENASSETIO_NS(StringView) * error, double* out,
              OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key);

  /**
   * Retrieve a string value from the map.
   *
   * Missing values will result in a @fqcref{ErrorCode_kOutOfRange} error
   * code.
   *
   * Values with the wrong data type will result in a
   * @fqcref{ErrorCode_kBadVariantAccess} error code.
   *
   * An `out` parameter with insufficient capacity for the string value
   * will result in truncation of the string as well as a
   * @fqcref{ErrorCode_kLengthError} error code.
   *
   * @param[out] error Storage for error message, if any.
   * @param[out] out Storage for retrieved value.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to query.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*getStr)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(StringView) * out,
            OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key);
} OPENASSETIO_NS(InfoDictionary_s);

/**
 * Get an instance of a @fqcref{InfoDictionary_s} "InfoDictionary suite" of C API
 * function pointers.
 *
 * @return Suite of function pointers.
 */
OPENASSETIO_CORE_C_EXPORT OPENASSETIO_NS(InfoDictionary_s) OPENASSETIO_NS(InfoDictionary_suite)();

/**
 * @}
 */
#ifdef __cplusplus
}
#endif
