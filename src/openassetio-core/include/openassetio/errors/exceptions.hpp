// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <stdexcept>
#include <string>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace errors {
/**
 * @name OpenassetIO Exceptions
 *
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
 * @}
 */
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
