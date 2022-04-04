// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
/**
 * Throw the appropriate exception for given error code, if any.
 *
 * @todo Establish a mapping of code to exception type - currently
 *  everything is a `runtime_error`.
 *
 * @param code Error code.
 * @param msg Error message to bundle in exception.
 */
inline void throwIfError(
    const int code,
    [[maybe_unused]] const OPENASSETIO_NS(SimpleString) & msg) {
  if (code != 0) {
    Str errorMessageWithCode = std::to_string(code);
    errorMessageWithCode += ": ";
    errorMessageWithCode += std::string_view{msg.buffer, msg.usedSize};
    throw std::runtime_error(errorMessageWithCode);
  }
}
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
