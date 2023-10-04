// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <optional>
#include <string>

#include <openassetio/EntityReference.hpp>
#include <openassetio/access.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/internal.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace errors {
/**Get an error code name as a printable string*/
Str errorCodeName(BatchElementError::ErrorCode code);

/**Construct a full message to place into a convenience exception.*/
std::string createBatchElementExceptionMessage(const BatchElementError& err, size_t index,
                                               const EntityReference& entityReference,
                                               internal::access::Access access);
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
