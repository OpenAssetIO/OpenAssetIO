// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <stdbool.h>  // NOLINT(modernize-deprecated-headers)
#include <stddef.h>   // NOLINT(modernize-deprecated-headers)
#include <stdint.h>   // NOLINT(modernize-deprecated-headers)

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
 * @defgroup CInfoDictionary InfoDictionary
 *
 * C API for the \fqref{InfoDictionary} "InfoDictionary C++ type".
 *
 * @{
 */

// Symbol namespacing.
#define oa_InfoDictionary_t OPENASSETIO_NS(InfoDictionary_t)
#define oa_InfoDictionary_h OPENASSETIO_NS(InfoDictionary_h)
#define oa_InfoDictionary_ValueType_kBool OPENASSETIO_NS(InfoDictionary_ValueType_kBool)
#define oa_InfoDictionary_ValueType_kInt OPENASSETIO_NS(InfoDictionary_ValueType_kInt)
#define oa_InfoDictionary_ValueType_kFloat OPENASSETIO_NS(InfoDictionary_ValueType_kFloat)
#define oa_InfoDictionary_ValueType_kStr OPENASSETIO_NS(InfoDictionary_ValueType_kStr)
#define oa_InfoDictionary_ValueType OPENASSETIO_NS(InfoDictionary_ValueType)
#define oa_InfoDictionary_ctor OPENASSETIO_NS(InfoDictionary_ctor)
#define oa_InfoDictionary_dtor OPENASSETIO_NS(InfoDictionary_dtor)
#define oa_InfoDictionary_size OPENASSETIO_NS(InfoDictionary_size)
#define oa_InfoDictionary_typeOf OPENASSETIO_NS(InfoDictionary_typeOf)
#define oa_InfoDictionary_getBool OPENASSETIO_NS(InfoDictionary_getBool)
#define oa_InfoDictionary_getInt OPENASSETIO_NS(InfoDictionary_getInt)
#define oa_InfoDictionary_getFloat OPENASSETIO_NS(InfoDictionary_getFloat)
#define oa_InfoDictionary_getStr OPENASSETIO_NS(InfoDictionary_getStr)
#define oa_InfoDictionary_setBool OPENASSETIO_NS(InfoDictionary_setBool)
#define oa_InfoDictionary_setInt OPENASSETIO_NS(InfoDictionary_setInt)
#define oa_InfoDictionary_setFloat OPENASSETIO_NS(InfoDictionary_setFloat)
#define oa_InfoDictionary_setStr OPENASSETIO_NS(InfoDictionary_setStr)

/**
 * Opaque handle type representing a @fqref{InfoDictionary}
 * "InfoDictionary" instance.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct oa_InfoDictionary_t* oa_InfoDictionary_h;

/**
 * Enumeration of the available types in a @fqref{InfoDictionary}
 * "InfoDictionary".
 *
 * The set of possible types is dictated by those specified in the
 * definition of the @fqref{InfoDictionaryValue} "variant value type".
 * In particular, this means the set of types is fixed and cannot be
 * extended by hosts or plugins. This enum is therefore exhaustive.
 *
 * @see @fqcref{InfoDictionary_typeOf} "typeOf()"
 * @see @ref CppPrimitiveTypes "Primitive types"
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef enum {
  /// Boolean value type
  oa_InfoDictionary_ValueType_kBool = 1,
  /// Integer value type
  oa_InfoDictionary_ValueType_kInt,
  /// Floating point value type
  oa_InfoDictionary_ValueType_kFloat,
  /// String value type
  oa_InfoDictionary_ValueType_kStr
} oa_InfoDictionary_ValueType;

/**
 * Constructor function.
 *
 * The caller is responsible for deallocating via `dtor`.
 *
 * @param[out] error Storage for error message, if any.
 * @param[out] out Opaque handle to InfoDictionary.
 * @return Error code.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_ctor(oa_StringView* error,
                                                              oa_InfoDictionary_h* out);

/**
 * Destructor function.
 *
 * This should be called by the owner of the handle when the handle is
 * no longer in use. The underlying object will be destroyed and its
 * memory freed.
 *
 * @param handle Opaque handle to InfoDictionary.
 */
OPENASSETIO_CORE_C_EXPORT void oa_InfoDictionary_dtor(oa_InfoDictionary_h handle);

/**
 * Retrieve the number of entries currently in the map.
 *
 * @param handle Opaque handle to InfoDictionary.
 */
OPENASSETIO_CORE_C_EXPORT size_t oa_InfoDictionary_size(oa_InfoDictionary_h handle);  // noexcept

/**
 * Get the type of value stored in an entry.
 *
 * @param[out] error Storage for error message, if any.
 * @param[out] out Storage for retrieved type.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to query.
 * @return Error code.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_typeOf(oa_StringView* error,
                                                                oa_InfoDictionary_ValueType* out,
                                                                oa_InfoDictionary_h handle,
                                                                oa_ConstStringView key);

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_getBool(oa_StringView* error, bool* out,
                                                                 oa_InfoDictionary_h handle,
                                                                 oa_ConstStringView key);

/**
 * Retrieve an integer value from the map.
 *
 * @param[out] error Storage for error message, if any.
 * @param[out] out Storage for retrieved value.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to query.
 * @return Error code.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_getInt(oa_StringView* error, int64_t* out,
                                                                oa_InfoDictionary_h handle,
                                                                oa_ConstStringView key);

/**
 * Retrieve a floating point value from the map.
 *
 * @param[out] error Storage for error message, if any
 * @param[out] out Storage for retrieved value.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to query.
 * @return Error code.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_getFloat(oa_StringView* error,
                                                                  double* out,
                                                                  oa_InfoDictionary_h handle,
                                                                  oa_ConstStringView key);

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_getStr(oa_StringView* error,
                                                                oa_StringView* out,
                                                                oa_InfoDictionary_h handle,
                                                                oa_ConstStringView key);
/// @}
// Accessors

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
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_setBool(oa_StringView* error,
                                                                 oa_InfoDictionary_h handle,
                                                                 oa_ConstStringView key,
                                                                 bool value);
/**
 * Set an integer value in the map.
 *
 * @param[out] error Storage for error message, if any.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to mutate.
 * @param value Value to set in entry.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_setInt(oa_StringView* error,
                                                                oa_InfoDictionary_h handle,
                                                                oa_ConstStringView key,
                                                                int64_t value);

/**
 * Set a floating point value in the map.
 *
 * @param[out] error Storage for error message, if any.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to mutate.
 * @param value Value to set in entry.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_setFloat(oa_StringView* error,
                                                                  oa_InfoDictionary_h handle,
                                                                  oa_ConstStringView key,
                                                                  double value);

/**
 * Set a string value in the map.
 *
 * @param[out] error Storage for error message, if any.
 * @param handle Opaque handle to InfoDictionary.
 * @param key Key of entry to mutate.
 * @param value Value to set in entry.
 */
OPENASSETIO_CORE_C_EXPORT oa_ErrorCode oa_InfoDictionary_setStr(oa_StringView* error,
                                                                oa_InfoDictionary_h handle,
                                                                oa_ConstStringView key,
                                                                oa_ConstStringView value);

/// @}
// Mutators
/// @}
// CInfoDictionary
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
