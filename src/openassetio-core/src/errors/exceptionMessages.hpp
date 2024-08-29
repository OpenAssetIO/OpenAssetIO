// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <optional>
#include <string>

#include <openassetio/EntityReference.hpp>
#include <openassetio/access.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/internal.hpp>
#include <openassetio/trait/collection.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace errors {
/**Get an error code name as a printable string*/
Str errorCodeName(BatchElementError::ErrorCode code);

/**Construct a full message to place into a convenience exception.*/
Str createBatchElementExceptionMessage(const BatchElementError& err, size_t index,
                                       std::optional<internal::access::Access> access,
                                       const std::optional<EntityReference>& entityReference,
                                       const std::optional<trait::TraitSet>& traitSet);
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
