// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <stdexcept>
#include <string>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * This namespace contains types related to error handling.
 *
 * Generally there are two types of error handling, "standard" non-batch
 * error handling, which is exception based, and batch errors, which are
 * based upon the @ref BatchElementError type.
 *
 * All exceptions in OpenAssetIO are derived from the @ref
 * OpenAssetIOException type, the idea being a host can use this as a
 * catch-all exception type when attempting mitigative exception
 * handling.
 *
 * Batch error handling with @ref BatchElementError is not
 * exceptional, However, OpenAssetIO provides convenience wrappers
 * around some batch functions that makes them exceptional, therefore
 * @ref BatchElementError is converted to its twin,
 * @ref BatchElementException, also found in this namespace.
 */
namespace errors {

/**
 * @name OpenassetIO Exceptions
 * @{
 */

/**
 * Exception base for all OpenAssetIO exceptions.
 *
 * Should normally not be constructed directly, favour the more fully
 * derived exceptions instead.
 */
struct OPENASSETIO_CORE_EXPORT OpenAssetIOException : std::runtime_error {
  using std::runtime_error::runtime_error;
};

/**
 * Thrown whenever the input to a public API function is invalid for the
 * requested operation.
 */
struct OPENASSETIO_CORE_EXPORT InputValidationException : OpenAssetIOException {
  using OpenAssetIOException::OpenAssetIOException;
};

/**
 * A special case of InputValidationException for cases where the input
 * comes from external config, rather than function arguments.
 *
 * Thrown whenever a procedure must abort due to misconfigured
 * user-provided configuration, often relating to the plugin system.
 */
struct OPENASSETIO_CORE_EXPORT ConfigurationException : InputValidationException {
  using InputValidationException::InputValidationException;
};

/**
 * Thrown whenever a procedure must abort due to not being implemented.
 * Many methods in OpenAssetIO are optionally implementable, and some
 * may throw this exception to indicate that calling them constitutes
 * an error.
 */
struct OPENASSETIO_CORE_EXPORT NotImplementedException : OpenAssetIOException {
  using OpenAssetIOException::OpenAssetIOException;
};

/**
 * Exceptions emitted from manager plugins that are not handled will
 * be converted to this type and re-thrown when the exception passes
 * through the OpenAssetIO middleware.
 */
struct OPENASSETIO_CORE_EXPORT UnhandledException : OpenAssetIOException {
  using OpenAssetIOException::OpenAssetIOException;
};

/**
 * Exception thrown when a @ref BatchElementError is converted.
 *
 * Not a type that a manager should throw, exclusively thrown via the
 * middleware when the user is calling an exceptional convenience and a
 * @ref BatchElementError is emitted by the manager.
 */
struct OPENASSETIO_CORE_EXPORT BatchElementException : OpenAssetIOException {
  BatchElementException(std::size_t idx, BatchElementError err, const std::string& message)
      : OpenAssetIOException{message}, index{idx}, error{std::move(err)} {}

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
 * @}
 */
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
