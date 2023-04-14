// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <stdexcept>
#include <string>
#include <utility>

#include <openassetio/errors.h>
#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * @name Batch element errors
 *
 * @{
 */
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
     * Error code used whenever an entity reference is not one that
     * is known to the manager.
     *
     * In the case of a manager that uses standard URIs, then it
     * could be that the scheme is that of another manager.
     */
    kInvalidEntityReference = OPENASSETIO_BatchErrorCode_kInvalidEntityReference,

    /**
     * Error code used whenever an entity-based action is performed on
     * a malformed @ref entity_reference.
     *
     * Entity references are initially validated as part of constructing
     * an @fqref{EntityReference} "EntityReference" object. However,
     * that is a naive check intended to validate the general format of
     * a reference string is one belonging to the manager. It does not
     * validate that all aspects of the reference are valid, as that may
     * be situational, based on the target entity and the context of the
     * API call.
     *
     * For example, assuming entity references are encoded as URIs, a
     * `kMalformedEntityReference` could indicate that a required query
     * parameters is missing for a given operation, or a supplied
     * parameter is not relevant to that particular operation/entity.
     */
    kMalformedEntityReference = OPENASSETIO_BatchErrorCode_kMalformedEntityReference,

    /**
     * Error code used when the reference is valid, but the supplied
     * @ref Context access is invalid for the operation. A common
     * example of this would be resolving a read-only entity with a
     * write access Context, or during @ref preflight or @ref register
     * when the target entity s read-only and does not support
     * versioning.
     */
    kEntityAccessError = OPENASSETIO_BatchErrorCode_kEntityAccessError,

    /**
     * Error code used during @ref resolve "entity resolution" when the
     * reference itself is valid, but it is not possible to retrieve
     * data for the referenced @ref entity.
     *
     * This could be because it does not exist, or some other
     * entity-specific reason that this data cannot be resolved for a
     * specific entity. This code should not be used if an entity does
     * not have a requested trait - simply do not set that trait in the
     * resulting data. Fatal runtime errors during resolution (eg:
     * server connection errors) should be raised as exceptions, rather
     * than per-entity errors.
     *
     * This code is also used during version finalisation and any other
     * entity-based operations on a valid @ref entity_reference that
     * fail for some reason.
     */
    kEntityResolutionError = OPENASSETIO_BatchErrorCode_kEntityResolutionError
  };

  /**
   * Compares two instances to see if they match.
   *
   * @return `true` if the batch elements errors match, otherwise `false`.
   */
  constexpr bool operator==(const BatchElementError& other) const {
    return code == other.code && message == other.message;
  }

  /**
   * Compares two instances to see if they do not match.
   *
   * @return `true` if the batch elements errors do not match, otherwise
   * `false`.
   */
  constexpr bool operator!=(const BatchElementError& other) const { return !(*this == other); }

  /// Error code indicating the class of error.
  ErrorCode code;
  /// Human-readable error message.
  Str message;
};

/**
 * Exception base that ties together a @ref BatchElementError and an
 * index.
 *
 * When thrown from a function, indicates that a particular
 * element has caused an error. The specific element that has errored
 * is indicated by the index attribute, relative to the input container.
 */
struct OPENASSETIO_CORE_EXPORT BatchElementException : std::runtime_error {
  BatchElementException(std::size_t idx, BatchElementError err)
      : std::runtime_error{err.message}, index{idx}, error{std::move(err)} {}

  /**
   * Index describing which batch element has caused an error.
   */
  std::size_t index;

  /**
   * Object describing the nature of the specific error.
   */
  BatchElementError error;
};

/**
 * Exception equivalent of
 * @ref BatchElementError.ErrorCode.kUnknown
 */
struct OPENASSETIO_CORE_EXPORT UnknownBatchElementException : BatchElementException {
  using BatchElementException::BatchElementException;
};

/**
 * Exception equivalent of
 * @ref BatchElementError.ErrorCode.kInvalidEntityReference
 */
struct OPENASSETIO_CORE_EXPORT InvalidEntityReferenceBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/**
 * Exception equivalent of
 * @ref BatchElementError.ErrorCode.kMalformedEntityReference
 */
struct OPENASSETIO_CORE_EXPORT MalformedEntityReferenceBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/**
 * Exception equivalent of
 * @ref BatchElementError.ErrorCode.kEntityAccessError
 */
struct OPENASSETIO_CORE_EXPORT EntityAccessErrorBatchElementException : BatchElementException {
  using BatchElementException::BatchElementException;
};

/**
 * Exception equivalent of
 * @ref BatchElementError.ErrorCode.kEntityResolutionError
 */
struct OPENASSETIO_CORE_EXPORT EntityResolutionErrorBatchElementException : BatchElementException {
  using BatchElementException::BatchElementException;
};
/**
 * @}
 */
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
