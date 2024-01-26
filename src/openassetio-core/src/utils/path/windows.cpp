// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include "windows.hpp"

#include <algorithm>
#include <cassert>

#include <ada.h>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path::windows {

// ---------------------------------------------------------------------
// FileUrlPathConverter

Str FileUrlPathConverter::pathToUrl(const std::string_view& windowsPath) const {
  // Precondition.
  assert(!windowsPath.empty());

  ada::url url;
  // Note: url.set_protocol(...) is a no-op, see https://github.com/ada-url/ada/issues/573
  url.type = ada::scheme::FILE;

  if (!uncUnnormalisedDeviceSharePathHandler.toUrl(windowsPath, url)) {
    if (!uncUnnormalisedDeviceDrivePathHandler.toUrl(windowsPath, url)) {
      if (!uncSharePathHandler.toUrl(windowsPath, url)) {
        // If none of the above, assume a drive path, e.g. `C:\`
        drivePathHandler.toUrl(windowsPath, url);
      }
    }
  }

  return url.get_href();
}

Str FileUrlPathConverter::pathFromUrl(const std::string_view& url) const {
  ada::result<ada::url_aggregator> adaUrl = ada::parse(url);
  if (!adaUrl) {
    throwError(kErrorUrlParseFailure, url);
  }

  const std::string_view host = adaUrl->get_host();
  const std::string_view encodedPath = adaUrl->get_pathname();

  std::string_view trimmedPath = encodedPath;
  if (host.empty() && !encodedPath.empty()) {
    // E.g. path of `file:///C:/` is `/C:/`, so trim leading `/`.
    trimmedPath = encodedPath.substr(1);
  }

  Str decodedPath = ada::unicode::percent_decode(trimmedPath, trimmedPath.find(kPercent));

  // TODO(DF): Ordering of validation to satisfy error priority of
  // swift-url test cases.

  if (host.empty() && !driveLetterHandler.isAbsoluteDrivePath(decodedPath)) {
    throwError(kErrorRelativePath, url);
  }
  if (GenericPath::containsNullByte(decodedPath)) {
    throwError(kErrorNullByte, url);
  }
  if (urlHandler.containsPercentEncodedSlash(encodedPath)) {
    throwError(kErrorEncodedSeparator, url);
  }
  if (!host.empty() && uncHostHandler.isInvalidHostname(host)) {
    throwError(kErrorUnsupportedHostname, url);
  }

  Str windowsPath;
  if (!host.empty()) {
    windowsPath += kDoubleBackSlash;
    if (const auto ip6Host = urlHandler.ip6ToValidHostname(host)) {
      windowsPath += *ip6Host;
    } else {
      windowsPath += host;
    }
  }

  decodedPath =
      forwardSlashSeparatedStringHandler.removeTrailingForwardSlashesInPathSegments(decodedPath);
  windowsPath += decodedPath;

  std::replace(windowsPath.begin(), windowsPath.end(), kForwardSlash, kBackSlash);

  return windowsPath;
}
}  // namespace utils::path::windows
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
