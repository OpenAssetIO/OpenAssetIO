// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <cstddef>

#include "./namespace.h"

#ifdef __cplusplus
extern "C" {
#endif
/**
 * @addtogroup CAPI C API
 * @{
 */

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
 * use the `buffer` member directly where a null-terminated string is
 * expected.
 *
 * When used as an out-parameter, the caller must allocate a `char*`
 * buffer and initialize the `StringView` with the maximum number of
 * `char` elements, the buffer pointer itself, and a used size of zero,
 * e.g.
 *
 * @code{.c}
 * char myBuffer[500];
 *
 * OPENASSETIO_NS(StringView) myDestString {
 *   500, myBuffer, 0
 * };
 *
 * myUpdateString(&myDestString);
 * @endcode
 *
 * The callee should then write to the `buffer`, up to a maximum of
 * `maxSize` elements, and update the `usedSize` with the number of
 * elements used, e.g.
 *
 * @code{.c}
 * void myUpdateString(OPENASSETIO_NS(StringView)* myDestString) {
 *
 *   myDestString->usedSize =
 *     min(myDestString->maxSize, mySrcStringSize);
 *
 *   strncpy(myDestString->buffer, mySrcString, myDestString->usedSize);
 * }
 * @endcode
 */
// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  /// Number of available elements in buffer.
  const size_t maxSize;
  /// Writeable buffer storing the string data.
  char* buffer;
  /// Number of elements in the buffer used for string storage.
  size_t usedSize;
} OPENASSETIO_NS(StringView);

/**
 * @}
 */
#ifdef __cplusplus
}
#endif
