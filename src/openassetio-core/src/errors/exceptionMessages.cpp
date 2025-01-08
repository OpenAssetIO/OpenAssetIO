// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd

#include "exceptionMessages.hpp"

#include <cassert>
#include <cstddef>
#include <optional>

#include <fmt/core.h>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/access.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/internal.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

#include "../utils/formatter.hpp"

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
    case BatchElementError::ErrorCode::kAuthError:
      return "authError";
  }

  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(false);  // Impossible case.
  return "Unknown ErrorCode";
}

Str createBatchElementExceptionMessage(const BatchElementError& err, std::size_t index,
                                       const std::optional<internal::access::Access> access,
                                       const std::optional<EntityReference>& entityReference,
                                       const std::optional<trait::TraitSet>& traitSet) {
  /*
   * BatchElementException messages consist of five parts.
   * 1. The name of the error code.
   * 2. The message inside the BatchElementError.
   * 3. The index that the batch error relates to.
   * 4. The access mode.
   * 5. The entity reference.
   * 6. The trait set.
   *
   * Ends up looking something like : "entityAccessError: Could not
   * access Entity [index=2] [access=read] [entity=bal:///entityRef]"
   */
  Str result;

  result += fmt::format("{}:", errorCodeName(err.code));

  if (!err.message.empty()) {
    result += " ";
    result += err.message;
  }

  result += fmt::format(" [index={}]", index);

  if (access) {
    result += fmt::format(" [access={}]", access::kAccessNames[*access]);
  }

  if (entityReference) {
    result += fmt::format(" [entity={}]", entityReference->toString());
  }

  if (traitSet) {
    result += fmt::format(" [traits={}]", *traitSet);
  }

  return result;
}
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
