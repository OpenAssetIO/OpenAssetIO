// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include "detail.hpp"

#include <algorithm>
#include <cassert>

#include "../common.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path::windows::detail {

// ---------------------------------------------------------------------
// WindowsUrl

bool WindowsUrl::containsPercentEncodedSlash(const std::string_view& url) const {
  // Using regex for case-insensitivity.
  return percentEncodedSlashRegex.match(url).has_value();
}

std::optional<Str> WindowsUrl::ip6ToValidHostname(const std::string_view& host) const {
  auto match = ip6HostRegex.match(host);
  if (!match) {
    return std::nullopt;
  }
  Str ip6HostName;
  ip6HostName = match->group(host, 1);
  ip6HostName += kIp6HostSuffix;
  std::replace(ip6HostName.begin(), ip6HostName.end(), kColon, kHyphen);
  return ip6HostName;
}

bool WindowsUrl::maybePercentEncodeAndAppendTo(const std::string_view& path, Str& appendTo) {
  // Ada will automatically %-encode upon setting the URL path, but
  // with a more limited set than we want.
  // TODO(DF): Ideally we'd use `percent_encode<true>`, which appends
  // to a given string if encoding is needed. However, that
  // specialisation is not generated in ada v2.7.4 on MacOS/clang and
  // fails to link. See https://github.com/ada-url/ada/issues/580
  Str result;
  if (ada::unicode::percent_encode<false>(path, kPercentEncodeCharacterSet.data(), result)) {
    appendTo += result;
    return true;
  }
  return false;
}

bool WindowsUrl::setUrlHost(const std::string_view& host, ada::url& url) const {
  if (localHostRegex.match(host).has_value()) {
    return url.set_host(kLocalHostIP);
  }
  return url.set_host(host);
}

// ---------------------------------------------------------------------
// NormalisedPath

std::string_view NormalisedPath::withoutTrailingSlashes(const std::string_view& path) const {
  auto match = trailingSlashesRegex.match(path);
  if (!match) {
    return path;
  }
  return path.substr(0, path.size() - match->group(path, 1).size());
}

std::string_view NormalisedPath::withoutTrailingDotsAsFile(const std::string_view& path) const {
  auto match = trailingDotsAsFileRegex.match(path);
  if (!match) {
    return path;
  }
  return path.substr(0, path.size() - match->group(path, 1).size());
}

std::string_view NormalisedPath::withoutTrailingDotsInFile(const std::string_view& path) const {
  auto match = trailingDotsInFileRegex.match(path);
  if (!match) {
    return path;
  }
  return path.substr(0, path.size() - match->group(path, 1).size());
}

std::string_view NormalisedPath::withoutTrailingSpacesAndDots(const std::string_view& path) const {
  auto match = trailingDotsAndSpacesRegex.match(path);
  if (!match) {
    return path;
  }
  return path.substr(0, path.size() - match->group(path, 1).size());
}

bool NormalisedPath::containsUpwardsTraversal(const std::string_view& path) const {
  return upwardsTraversalRegex.match(path).has_value();
}

Str NormalisedPath::removeTrailingDotsInPathSegments(const std::string_view& path) const {
  return trailingSingleDotInSegmentRegex.substituteToReduceSize(path, "");
}

Str NormalisedPath::removeTrailingSlashesInPathSegments(const std::string_view& path) const {
  return trailingSlashesInSegmentRegex.substituteToReduceSize(path, kBackSlashStr);
}

bool NormalisedPath::startsWithSlash(const std::string_view& path) {
  // Precondition.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(!path.empty());
  return path.substr(0, 1).find_first_of(kAnySlash) != std::string_view::npos;
}

// ---------------------------------------------------------------------
// DriveLetter

bool DriveLetter::isDrive(const std::string_view& str) const {
  return driveRegex.match(str).has_value();
}

bool DriveLetter::isAbsoluteDrivePath(const std::string_view& str) const {
  return absoluteDrivePathRegex.match(str).has_value();
}

// ---------------------------------------------------------------------
// UncHost

bool UncHost::isInvalidHostname(const std::string_view& host) const {
  return invalidHostnameRegex.match(host).has_value();
}

// ---------------------------------------------------------------------
// UncUnnormalisedDevicePath

void UncUnnormalisedDevicePath::validatePath(const std::string_view& windowsPath,
                                             const UncDetails& uncDetails) const {
  if (uncDetails.fullPath.empty()) {
    // Must have something after the `\\?\` or `\\?\UNC\`
    throwError(kErrorInvalidPath, windowsPath);
  }
  if (containsForwardSlash(uncDetails.fullPath)) {
    // Don't support verbatim `/` in UNC device paths, for now.
    throwError(kErrorUnsupportedDevicePath, windowsPath);
  }
  if (containsUpwardsTraversal(uncDetails.shareNameAndPath)) {
    // Disallow `..`, except for hostnames.
    throwError(kErrorUpwardsTraversal, windowsPath);
  }
}

std::string_view UncUnnormalisedDevicePath::withoutTrailingSlashes(
    const std::string_view& path) const {
  auto match = trailingSlashesRegex.match(path);
  if (!match) {
    return path;
  }
  return path.substr(0, path.size() - match->group(path, 1).size());
}

bool UncUnnormalisedDevicePath::containsForwardSlash(const std::string_view& path) {
  return path.find_first_of(kForwardSlash) != std::string_view::npos;
}

bool UncUnnormalisedDevicePath::containsUpwardsTraversal(const std::string_view& str) const {
  return upwardsTraversalRegex.match(str).has_value();
}

Str UncUnnormalisedDevicePath::removeTrailingSlashesInPathSegments(
    const std::string_view& path) const {
  return trailingSlashesInSegmentRegex.substituteToReduceSize(path, R"(\)");
}

}  // namespace utils::path::windows::detail
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
