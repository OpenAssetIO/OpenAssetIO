// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2024 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/typedefs.hpp>

#include "StringView.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace errors {
/**
 * Throw the appropriate exception for given error code, if any.
 *
 * @param code Error code.
 * @param msg Error message to bundle in exception.
 */
inline void throwIfError(const oa_ErrorCode code, [[maybe_unused]] const oa_StringView &msg) {
  if (code != oa_ErrorCode_kOK) {
    Str errorMessageWithCode = std::to_string(code);
    errorMessageWithCode += ": ";
    errorMessageWithCode += std::string_view{msg.data, msg.size};
    throw errors::OpenAssetIOException(errorMessageWithCode);
  }
}

/**
 * Extract message from an exception and copy into a C StringView
 * out-param.
 *
 * If `err` has insufficient `capacity` to hold the exception's
 * description string, then the string is truncated at `capacity`
 * bytes.
 *
 * @tparam Exception Exception type to extract from.
 * @param err String storage to copy exception message to.
 * @param exc Exception to extract message from.
 */
template <class Exception>
void extractExceptionMessage(oa_StringView *err, const Exception &exc) {
  openassetio::assignStringView(err, exc.what());
}

/**
 * Wrap a callable such that all exceptions are caught and converted to
 * an error code.
 *
 * This is intended as a fallback for unhandled exceptions.
 *
 * @tparam Fn Type of callable to wrap.
 * @param err Storage for error message, if any.
 * @param callable Callable to wrap.
 * @return Error code.
 */
template <typename Fn>
auto catchUnknownExceptionAsCode(oa_StringView *err, Fn &&callable) {
  try {
    return callable();
  } catch (std::exception &exc) {
    extractExceptionMessage(err, exc);
    return oa_ErrorCode_kException;
  } catch (...) {
    assignStringView(err, "Unknown non-exception object thrown");
    return oa_ErrorCode_kUnknown;
  }
}
}  // namespace errors
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
