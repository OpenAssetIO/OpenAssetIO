// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include "posix.hpp"

#include <cassert>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path::posix {

Str FileUrlPathConverter::pathToUrl(const std::string_view& posixPath) const {
  // Precondition.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(!posixPath.empty());

  if (posixPathHandler.containsUpwardsTraversal(posixPath)) {
    throwError(kErrorUpwardsTraversal, posixPath);
  }
  if (!detail::PosixPath::startsWithForwardSlash(posixPath)) {
    throwError(kErrorRelativePath, posixPath);
  }

  ada::url adaUrl;
  adaUrl.type = ada::scheme::FILE;
  // Must explicitly set empty host to get `file://` rather than
  // `file:`.
  adaUrl.set_host("");

  const Str processedPath = [&] {
    if (auto encodedPath = detail::PosixUrl::maybePercentEncode(posixPath)) {
      return posixPathHandler.removeTrailingForwardSlashesInPathSegments(*encodedPath);
    }
    return posixPathHandler.removeTrailingForwardSlashesInPathSegments(posixPath);
  }();

  if (!adaUrl.set_pathname(processedPath)) {
    throwError(kErrorInvalidUrlPath, posixPath);
  }

  return adaUrl.get_href();
}

Str FileUrlPathConverter::pathFromUrl(const std::string_view& url) const {
  ada::result<ada::url_aggregator> adaUrl = ada::parse(url);
  if (!adaUrl) {
    throwError(kErrorUrlParseFailure, url);
  }

  if (!adaUrl->get_host().empty()) {
    throwError(kErrorNonLocal, url);
  }

  const std::string_view path = adaUrl->get_pathname();

  if (urlHandler.containsPercentEncodedForwardSlash(path)) {
    throwError(kErrorEncodedSeparator, url);
  }

  const Str decodedPath = ada::unicode::percent_decode(path, path.find(kPercent));

  if (GenericPath::containsNullByte(decodedPath)) {
    throwError(kErrorNullByte, url);
  }

  return posixPathHandler.removeTrailingForwardSlashesInPathSegments(decodedPath);
}
}  // namespace utils::path::posix
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
