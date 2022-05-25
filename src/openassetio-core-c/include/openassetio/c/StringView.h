// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <stddef.h>  // NOLINT(modernize-deprecated-headers)

#include "./namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

/**
 * @defgroup oa_StringView oa_StringView
 *
 * C API for views on character buffers.
 *
 * @{
 */

/**
 * @defgroup oa_StringView_aliases Aliases
 *
 * @{
 */
#define oa_ConstStringView OPENASSETIO_NS(ConstStringView)
#define oa_StringView OPENASSETIO_NS(StringView)

/// @}
// oa_StringView_aliases

/**
 * Immutable string view struct.
 *
 * This type presents an immutable view on a pre-existing character
 * buffer.
 *
 * It is important that the underlying buffer is treated as opaque and
 * not written to after the `ConstStringView` has been constructed.
 *
 * The underlying buffer is expected to remain valid for at least as
 * long as the `ConstStringView` is in use.
 *
 * Since the struct stores the used size, null-termination is not
 * required, facilitating a wider range of string sources (e.g. from
 * non-C based languages). This also avoids the need to re-measure the
 * string's size as it is passed around.
 *
 * @warning Since null-termination cannot be assumed, it is unsafe to
 * use the `data` member directly where a null-terminated string is
 * expected.
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /// Immutable buffer storing the string data.
  const char* const data;
  /// Number of bytes used for string storage in the buffer.
  const size_t size;
} oa_ConstStringView;

/**
 * Mutable string view struct useful for out-parameters.
 *
 * This type presents a mutable view on a pre-existing character buffer.
 *
 * It is important that the underlying buffer is treated as opaque and
 * not read or written to directly, but instead only through the
 * `StringView`.
 *
 * The underlying buffer is expected to remain valid for at least as
 * long as the `StringView` is in use.
 *
 * Since the struct stores the used size, null-termination is not
 * required, facilitating a wider range of string sources (e.g. from
 * non-C based languages). This also avoids the need to re-measure the
 * string's size as it is passed around.
 *
 * @warning Since null-termination cannot be assumed, it is unsafe to
 * use the `data` member directly where a null-terminated string is
 * expected.
 *
 * When used as an out-parameter, the caller must allocate a `char*`
 * buffer and initialize the `StringView` with the maximum number of
 * `char` bytes, the buffer pointer itself, and a used size of zero,
 * e.g.
 *
 * @code{.c}
 * char myBuffer[500];
 *
 * oa_StringView myDestString {
 *   500, myBuffer, 0
 * };
 *
 * myUpdateString(&myDestString);
 * @endcode
 *
 * The callee should then write to the `data`, up to a maximum of
 * `capacity` bytes, and update the `size` with the number of
 * bytes used, e.g.
 *
 * @code{.c}
 * void myUpdateString(oa_StringView* myDestString) {
 *
 *   myDestString->size =
 *     min(myDestString->capacity, mySrcStringSize);
 *
 *   strncpy(myDestString->data, mySrcStringData, myDestString->size);
 * }
 * @endcode
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /// Number of bytes available for string storage in the buffer.
  const size_t capacity;
  /// Writeable buffer storing the string data.
  char* const data;
  /// Number of bytes used for string storage in the buffer.
  size_t size;
} oa_StringView;

/// @}
// oa_StringView
/// @}
// CAPI
#ifdef __cplusplus
}
#endif
