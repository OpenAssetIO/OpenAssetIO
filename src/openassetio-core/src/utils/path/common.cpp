// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include "common.hpp"

#include <string_view>

#include <ada/url.h>
#include <fmt/core.h>

#include <openassetio/export.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path {

void throwError(const std::string_view message, const std::string_view pathOrUrl) {
  throw errors::InputValidationException(fmt::format("{} ('{}')", message, pathOrUrl));
}

// ---------------------------------------------------------------------
// ForwardSlashSeparatedString

Str ForwardSlashSeparatedString::removeTrailingForwardSlashesInPathSegments(
    const std::string_view& str) const {
  return trailingForwardSlashesInSegmentRegex.substituteToReduceSize(str, "/");
}

// ---------------------------------------------------------------------
// GenericUrl

bool GenericUrl::isFileUrl(const std::string_view& url) const {
  return fileUrlRegex.match(url).has_value();
}

void GenericUrl::setUrlPath(const Str& urlPath, ada::url& url) {
  if (!url.set_pathname(urlPath)) {
    // This exception is unexpected. All validation leading to this
    // point should mean the above method always succeeds.
    throwError(kErrorInvalidUrlPath, urlPath);
  }
}
}  // namespace utils::path
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
