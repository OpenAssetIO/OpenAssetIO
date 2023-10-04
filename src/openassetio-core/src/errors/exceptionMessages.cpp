// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include "exceptionMessages.hpp"

#include <cassert>

#include <fmt/core.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace errors {

Str errorCodeName(BatchElementError::ErrorCode code) {
  switch (code) {
    case BatchElementError::ErrorCode::kUnknown:
      return "unknown";
    case BatchElementError::ErrorCode::kInvalidEntityReference:
      return "invalidEntityReference";
    case BatchElementError::ErrorCode::kMalformedEntityReference:
      return "malformedEntityReference";
    case BatchElementError::ErrorCode::kEntityAccessError:
      return "entityAccessError";
    case BatchElementError::ErrorCode::kEntityResolutionError:
      return "entityResolutionError";
    case BatchElementError::ErrorCode::kInvalidPreflightHint:
      return "invalidPreflightHint";
    case BatchElementError::ErrorCode::kInvalidTraitSet:
      return "invalidTraitSet";
  }

  assert(false);  // Impossible case.
  return "Unknown ErrorCode";
}

std::string createBatchElementExceptionMessage(const BatchElementError& err, size_t index,
                                               const EntityReference& entityReference,
                                               internal::access::Access access) {
  /*
   * BatchElementException messages consist of five parts.
   * 1. The name of the error code.
   * 2. The message inside the BatchElementError.
   * 3. The index that the batch error relates to.
   * 4. The access mode.
   * 5. The entity reference.
   *
   * Ends up looking something like : "entityAccessError: Could not
   * access Entity [index=2] [access=read] [entity=bal:///entityRef]"
   */
  const auto errorCodeStr = fmt::format("{}:", errorCodeName(err.code));
  const auto errorMessageStr = err.message.empty() ? "" : fmt::format(" {}", err.message);

  // Data elements
  const auto indexStr = fmt::format(" [index={}]", index);
  const auto accessStr = fmt::format(" [access={}]", access::kAccessNames[access]);
  const auto entityReferenceStr = fmt::format(" [entity={}]", entityReference.toString());

  return fmt::format("{}{}{}{}{}", errorCodeStr, errorMessageStr, indexStr, accessStr,
                     entityReferenceStr);
}
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
