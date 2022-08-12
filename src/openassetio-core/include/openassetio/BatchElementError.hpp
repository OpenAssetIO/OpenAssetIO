// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <string>
#include <utility>

#include <openassetio/errors.h>
#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Structure representing per-element batch operation errors.
 *
 * Many OpenAssetIO API functions take multiple inputs, i.e. a batch of
 * elements, in order to allow the @ref manager backend to optimise bulk
 * queries. The results of such queries are usually returned
 * element-by-element via a callback.
 *
 * It is possible for the whole batch to fail due to some catastrophic
 * error, in which case a standard exception workflow is expected. Using
 * HTTP status codes as an analogy, a client error (4xx) would likely
 * correspond to a `BatchElementError`, whereas a server error (5xx)
 * would likely cause the whole batch to fail with an exception.
 *
 * However, it is also possible for a subset of elements in the batch to
 * fail, whilst the remainder succeed. An exception workflow doesn't
 * work so well here, and so every success callback is paired with an
 * error callback, allowing per-element errors to be communicated back
 * to the original caller (i.e. the @ref host application).
 *
 * The information for these per-element errors is bundled in instances
 * of this simple BatchElementError structure for passing to error
 * callbacks.
 *
 * This structure provides an error code, for control flow, and an
 * error message, for more (human-readable) detail.
 */
class BatchElementError final {
 public:
  /// Possible classes of error.
  enum class ErrorCode {
    /// Fallback for uncommon errors.
    kUnknown = OPENASSETIO_BatchErrorCode_kUnknown,
    /**
     * Error code used during @ref resolve "entity resolution" when the
     * reference itself is valid, but it is not possible to retrieve
     * data for the referenced @ref entity.
     *
     * This could be because it does not exist, or a read-only entity is
     * being resolved for write. This code should not be used if an
     * entity does not have a requested trait - simply do not set that
     * trait in the resulting data.
     *
     * This code is also used during version finalisation and any other
     * entity-based operations on a valid @ref entity_reference that
     * fail for some reason.
     */
    kEntityResolutionError = OPENASSETIO_BatchErrorCode_kEntityResolutionError,
  };

  /// Error code indicating the class of error.
  const ErrorCode code;
  /// Human-readable error message.
  const std::string message;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
