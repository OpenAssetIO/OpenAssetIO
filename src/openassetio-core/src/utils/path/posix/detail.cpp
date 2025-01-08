// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include "detail.hpp"

#include <cassert>
#include <optional>
#include <string_view>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

#include "../common.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path::posix::detail {

// ---------------------------------------------------------------------
// PosixPath

bool PosixPath::containsUpwardsTraversal(const std::string_view& str) const {
  return upwardsTraversalRegex.match(str).has_value();
}

bool PosixPath::startsWithForwardSlash(const std::string_view& path) {
  // Precondition
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(!path.empty());
  return path.front() == kForwardSlash;
}

Str PosixPath::removeTrailingForwardSlashesInPathSegments(const std::string_view& path) const {
  if (path.size() <= 2) {
    return Str{path};
  }
  Str normalisedPath;
  normalisedPath.reserve(path.size());
  // Apparently (according to swift-url code comments) two leading
  // `/`s are implementation defined, so should be retained. Any
  // more than two should be collapsed to one.
  if (path[0] == kForwardSlash && path[1] == kForwardSlash && path[2] != kForwardSlash) {
    const std::string_view pathView{path};
    normalisedPath += pathView.substr(0, 2);
    normalisedPath +=
        forwardSlashSeparatedStringHandler.removeTrailingForwardSlashesInPathSegments(
            pathView.substr(2));
  } else {
    normalisedPath =
        forwardSlashSeparatedStringHandler.removeTrailingForwardSlashesInPathSegments(path);
  }
  return normalisedPath;
}

// ---------------------------------------------------------------------
// PosixUrl

bool PosixUrl::containsPercentEncodedForwardSlash(const std::string_view& url) const {
  // Using regex for case-insensitivity.
  return percentEncodedForwardSlashRegex.match(url).has_value();
}

std::optional<Str> PosixUrl::maybePercentEncode(const std::string_view& path) {
  // Ada will automatically %-encode upon setting the URL path, but
  // with a more limited set than we want.
  Str encodedPath;
  if (ada::unicode::percent_encode<false>(path, kPercentEncodeCharacterSet.data(), encodedPath)) {
    return encodedPath;
  }
  return std::nullopt;
}
}  // namespace utils::path::posix::detail
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
