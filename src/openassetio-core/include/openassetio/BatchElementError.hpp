// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>

// Deprecated:
//  https://github.com/OpenAssetIO/OpenAssetIO/issues/1071
//  https://github.com/OpenAssetIO/OpenAssetIO/issues/1073

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
// 'typedef' allows attributes, 'using' does not
/// @deprecated see @fqref{errors.BatchElementError} "errors::BatchElementError"
// NOLINTNEXTLINE
OPENASSETIO_CORE_DEPRECATED typedef errors::BatchElementError BatchElementError;

/// @deprecated see @fqref{errors.BatchElementException}
struct OPENASSETIO_CORE_DEPRECATED_EXPORT BatchElementException : errors::BatchElementException {
  BatchElementException(std::size_t idx, errors::BatchElementError err)  // NOLINT
      : errors::BatchElementException(idx, err, err.message) {}
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT UnknownBatchElementException : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT InvalidEntityReferenceBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"

struct OPENASSETIO_CORE_DEPRECATED_EXPORT MalformedEntityReferenceBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT EntityAccessErrorBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT EntityResolutionErrorBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT InvalidPreflightHintBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};

/// @deprecated Removed, use @fqref{errors.BatchElementException} "errors::BatchElementException"
struct OPENASSETIO_CORE_DEPRECATED_EXPORT InvalidTraitSetBatchElementException
    : BatchElementException {
  using BatchElementException::BatchElementException;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
