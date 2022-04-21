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
 * Enumeration of the available types in a @fqref{InfoDictionary}
 * "InfoDictionary".
 *
 * The set of possible types is dictated by those specified in the
 * definition of the @fqref{InfoDictionaryValue} "variant value type".
 * In particular, this means the set of types is fixed and cannot be
 * extended by hosts or plugins. This enum is therefore exhaustive.
 *
 * @see @fqcref{InfoDictionary_s::typeOf} "typeOf"
 * @see @ref CppPrimitiveTypes "Primitive types"
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  /// Boolean value type
  OPENASSETIO_NS(InfoDictionary_ValueType_kBool) = 1,
  /// Integer value type
  OPENASSETIO_NS(InfoDictionary_ValueType_kInt),
  /// Floating point value type
  OPENASSETIO_NS(InfoDictionary_ValueType_kFloat),
  /// String value type
  OPENASSETIO_NS(InfoDictionary_ValueType_kStr)
} OPENASSETIO_NS(InfoDictionary_ValueType);

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
   * Retrieve the number of entries currently in the map.
   *
   * @param handle Opaque handle to InfoDictionary.
   */
  size_t (*size)(OPENASSETIO_NS(InfoDictionary_h) handle);  // noexcept

  /**
   * Get the type of value stored in an entry.
   *
   * @param[out] error Storage for error message, if any.
   * @param[out] out Storage for retrieved type.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to query.
   * @return Error code.
   */
  OPENASSETIO_NS(ErrorCode)
  (*typeOf)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_ValueType) * out,
            OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key);

  /**
   * @name Accessors
   *
   * Functions to retrieve values of a specific type at a given key in
   * a `InfoDictionary`.
   *
   * Missing values will result in a @fqcref{ErrorCode_kOutOfRange}
   * "kOutOfRange" error code.
   *
   * Values with the wrong data type will result in a
   * @fqcref{ErrorCode_kBadVariantAccess} "kBadVariantAccess" error
   * code.
   *
   * @{
   */

  /**
   * Retrieve a boolean value from the map.
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
   * An `out` parameter with insufficient capacity for the string value
   * will result in truncation of the string as well as a
   * @fqcref{ErrorCode_kLengthError} "kLengthError" error code.
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
  /**
   * @}
   */

  /**
   * @name Mutators
   *
   * Functions to set values of a specific type at a given key in
   * a `InfoDictionary`.
   *
   * If an entry already exists at the given key, it will be
   * overwritten. This works even if the previous value had a different
   * type.
   *
   * @{
   */

  /**
   * Set a boolean value in the map.
   *
   * @param[out] error Storage for error message, if any.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to mutate.
   * @param value  Value to set in entry.
   */
  OPENASSETIO_NS(ErrorCode)
  (*setBool)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_h) handle,
             const OPENASSETIO_NS(ConstStringView) key, const bool value);
  /**
   * Set an integer value in the map.
   *
   * @param[out] error Storage for error message, if any.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to mutate.
   * @param value Value to set in entry.
   */
  OPENASSETIO_NS(ErrorCode)
  (*setInt)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_h) handle,
            const OPENASSETIO_NS(ConstStringView) key, const int64_t value);

  /**
   * Set a floating point value in the map.
   *
   * @param[out] error Storage for error message, if any.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to mutate.
   * @param value Value to set in entry.
   */
  OPENASSETIO_NS(ErrorCode)
  (*setFloat)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_h) handle,
              const OPENASSETIO_NS(ConstStringView) key, const double value);
  /**
   * Set a string value in the map.
   *
   * @param[out] error Storage for error message, if any.
   * @param handle Opaque handle to InfoDictionary.
   * @param key Key of entry to mutate.
   * @param value Value to set in entry.
   */
  OPENASSETIO_NS(ErrorCode)
  (*setStr)(OPENASSETIO_NS(StringView) * error, OPENASSETIO_NS(InfoDictionary_h) handle,
            const OPENASSETIO_NS(ConstStringView) key,
            const OPENASSETIO_NS(ConstStringView) value);

  /**
   * @}
   */
} OPENASSETIO_NS(InfoDictionary_s);

/**
 * Get an instance of a @fqcref{InfoDictionary_s} "InfoDictionary suite"
 * of C API function pointers.
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
