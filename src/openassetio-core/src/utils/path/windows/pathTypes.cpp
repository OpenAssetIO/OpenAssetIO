// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include "pathTypes.hpp"

#include <algorithm>
#include <cassert>

#include "../common.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils::path::windows::pathTypes {

// ---------------------------------------------------------------------
// DrivePath

void DrivePath::toUrl(const std::string_view& windowsPath, ada::url& url) const {
  validatePath(windowsPath);
  // Must explicitly set empty host to get `file://` rather than
  // `file:`.
  url.set_host("");
  setUrlPath(windowsPath, url);
}

void DrivePath::validatePath(const std::string_view& windowsPath) const {
  // TODO(DF): Kludge to match error priority of swift-url. Otherwise
  // this would be handled by `isAbsoluteDrivePath`.
  if (detail::NormalisedPath::startsWithSlash(windowsPath)) {
    // Path starts with slash so is a relative path.
    throwError(kErrorRelativePath, windowsPath);
  }
  if (normalisedPathHandler.containsUpwardsTraversal(windowsPath)) {
    // Path contains a `..` segment.
    throwError(kErrorUpwardsTraversal, windowsPath);
  }
  if (!driveLetterHandler.isAbsoluteDrivePath(windowsPath)) {
    // Path either isn't a drive path, or is a relative drive path
    // e.g. `C:` (without trailing slash).
    throwError(kErrorRelativePath, windowsPath);
  }
}

void DrivePath::setUrlPath(const std::string_view& windowsPath, ada::url& url) const {
  // Precondition.
  assert(driveLetterHandler.isAbsoluteDrivePath(windowsPath));

  // TODO(DF): This trimming logic could surely be optimised.
  const std::string_view trimmedPath = normalisedPathHandler.withoutTrailingDotsInFile(
      normalisedPathHandler.withoutTrailingDotsAsFile(
          normalisedPathHandler.withoutTrailingSpacesAndDots(
              normalisedPathHandler.withoutTrailingSlashes(windowsPath))));

  const Str normalisedPath = normalisedPathHandler.removeTrailingDotsInPathSegments(
      normalisedPathHandler.removeTrailingSlashesInPathSegments(trimmedPath));

  const std::string_view normalisedPathView{normalisedPath};
  const std::string_view driveLetter = normalisedPathView.substr(0, kDriveLetterLength);
  const std::string_view drivePath = normalisedPathView.substr(kDriveLetterLength);

  if (Str encodedPath{driveLetter};
      detail::WindowsUrl::maybePercentEncodeAndAppendTo(drivePath, encodedPath)) {
    GenericUrl::setUrlPath(encodedPath, url);
  } else {
    GenericUrl::setUrlPath(normalisedPath, url);
  }
}

// ---------------------------------------------------------------------
// UncSharePath

bool UncSharePath::toUrl(const std::string_view& windowsPath, ada::url& url) const {
  const std::optional<detail::UncDetails> uncDetails = extractUncDetails(windowsPath);
  if (!uncDetails) {
    return false;
  }
  validatePath(windowsPath, *uncDetails);
  if (!urlHandler.setUrlHost(uncDetails->hostOrDrive, url)) {
    throwError(kErrorInvalidHostname, windowsPath);
  }
  setUrlPath(*uncDetails, url);
  return true;
}

std::optional<detail::UncDetails> UncSharePath::extractUncDetails(
    const std::string_view& path) const {
  auto pathParts = pathRegex.match(path);
  if (!pathParts) {
    return std::nullopt;
  }
  const std::string_view prefix = pathParts->group(path, 1);
  const std::string_view hostOrDrive = pathParts->group(path, 2);
  const auto [shareName, sharePath, shareNameAndPath] =
      extractShareNameAndPath(pathParts->group(path, 3));
  const std::string_view fullPath =
      path.substr(prefix.size(), hostOrDrive.size() + shareNameAndPath.size());
  return detail::UncDetails{hostOrDrive, shareName, sharePath, shareNameAndPath, fullPath};
}

std::tuple<std::string_view, std::string_view, std::string_view>
UncSharePath::extractShareNameAndPath(std::string_view shareNameAndPath) const {
  shareNameAndPath = normalisedPathHandler.withoutTrailingSlashes(shareNameAndPath);
  auto headAndTail = pathHeadAndTailRegex.match(shareNameAndPath);
  if (!headAndTail) {
    // Share name without path.
    return {shareNameAndPath, {}, shareNameAndPath};
  }
  const std::string_view shareName = headAndTail->group(shareNameAndPath, 1);
  const std::string_view sharePath = normalisedPathHandler.withoutTrailingDotsInFile(
      normalisedPathHandler.withoutTrailingDotsAsFile(
          normalisedPathHandler.withoutTrailingSpacesAndDots(
              headAndTail->group(shareNameAndPath, 2))));
  // In case shareNameAndPath is now shorter due to trimming trailing
  // dots/spaces.
  shareNameAndPath = shareNameAndPath.substr(0, shareName.size() + sharePath.size());
  return {shareName, sharePath, shareNameAndPath};
}

void UncSharePath::validatePath(const std::string_view& windowsPath,
                                const detail::UncDetails& uncDetails) const {
  if (uncDetails.fullPath.empty()) {
    // Completely empty path after UNC prefix.
    throwError(kErrorInvalidPath, windowsPath);
  }
  if (normalisedPathHandler.containsUpwardsTraversal(uncDetails.shareNameAndPath)) {
    // Disallow `..`, except for hostnames.
    throwError(kErrorUpwardsTraversal, windowsPath);
  }
  if (uncHostHandler.isInvalidHostname(uncDetails.hostOrDrive)) {
    // E.g. non-ASCII or other disallowed character in hostname.
    throwError(kErrorInvalidHostname, windowsPath);
  }
}

void UncSharePath::setUrlPath(const detail::UncDetails& uncDetails, ada::url& url) const {
  Str normalisedPath;
  normalisedPath.reserve(uncDetails.shareNameAndPath.size());
  normalisedPath += uncDetails.shareName;
  normalisedPath += normalisedPathHandler.removeTrailingDotsInPathSegments(uncDetails.sharePath);
  normalisedPath = normalisedPathHandler.removeTrailingSlashesInPathSegments(normalisedPath);

  if (Str encodedPath;
      detail::WindowsUrl::maybePercentEncodeAndAppendTo(normalisedPath, encodedPath)) {
    GenericUrl::setUrlPath(encodedPath, url);
  } else {
    GenericUrl::setUrlPath(normalisedPath, url);
  }
}

// ---------------------------------------------------------------------
// UncUnnormalisedDeviceDrivePath

bool UncUnnormalisedDeviceDrivePath::toUrl(const std::string_view& windowsPath,
                                           ada::url& url) const {
  const std::optional<detail::UncDetails> uncDetails = extractUncDetails(windowsPath);
  if (!uncDetails) {
    return false;
  }
  validatePath(windowsPath, *uncDetails);
  url.set_host("");
  setUrlPath(*uncDetails, url);
  return true;
}

std::optional<detail::UncDetails> UncUnnormalisedDeviceDrivePath::extractUncDetails(
    const std::string_view& path) const {
  auto pathParts = pathRegex.match(path);
  if (!pathParts) {
    return std::nullopt;
  }
  const std::string_view hostOrDrive = pathParts->group(path, 1);
  const std::string_view shareNameAndPath =
      uncUnnormalisedDevicePathHandler.withoutTrailingSlashes(pathParts->group(path, 2));
  const std::string_view fullPath =
      path.substr(kPathPrefixLength, hostOrDrive.size() + shareNameAndPath.size());
  return detail::UncDetails{hostOrDrive, {}, {}, shareNameAndPath, fullPath};
}

void UncUnnormalisedDeviceDrivePath::validatePath(const std::string_view& windowsPath,
                                                  const detail::UncDetails& uncDetails) const {
  uncUnnormalisedDevicePathHandler.validatePath(windowsPath, uncDetails);

  // UNC device drive path specific

  if (uncDetails.hostOrDrive.empty()) {
    // E.g. `\\?\\path` - drive letter segment is blank.
    throwError(kErrorInvalidPath, windowsPath);
  }
  if (uncDetails.shareNameAndPath.empty()) {
    // Must be followed by an absolute path e.g. `\\?\C:\`.
    throwError(kErrorInvalidPath, windowsPath);
  }
  if (!driveLetterHandler.isDrive(uncDetails.hostOrDrive)) {
    // Must be followed by a drive e.g. `\\?\C:`.
    throwError(kErrorUnsupportedDevicePath, windowsPath);
  }
}

void UncUnnormalisedDeviceDrivePath::setUrlPath(const detail::UncDetails& uncDetails,
                                                ada::url& url) const {
  // `\\?\C:\path` - `C:` part should not be %-encoded.
  if (Str encodedPath{uncDetails.hostOrDrive}; detail::WindowsUrl::maybePercentEncodeAndAppendTo(
          uncUnnormalisedDevicePathHandler.removeTrailingSlashesInPathSegments(
              uncDetails.shareNameAndPath),
          encodedPath)) {
    GenericUrl::setUrlPath(
        uncUnnormalisedDevicePathHandler.removeTrailingSlashesInPathSegments(encodedPath), url);
  } else {
    GenericUrl::setUrlPath(
        uncUnnormalisedDevicePathHandler.removeTrailingSlashesInPathSegments(uncDetails.fullPath),
        url);
  }
}

// ---------------------------------------------------------------------
// UncUnnormalisedDeviceSharePath

bool UncUnnormalisedDeviceSharePath::toUrl(const std::string_view& windowsPath,
                                           ada::url& url) const {
  const std::optional<detail::UncDetails> uncDetails = extractUncDetails(windowsPath);
  if (!uncDetails) {
    return false;
  }
  validatePath(windowsPath, *uncDetails);
  if (!urlHandler.setUrlHost(uncDetails->hostOrDrive, url)) {
    throwError(kErrorInvalidHostname, windowsPath);
  }
  setUrlPath(*uncDetails, url);
  return true;
}

std::optional<detail::UncDetails> UncUnnormalisedDeviceSharePath::extractUncDetails(
    const std::string_view& path) const {
  auto pathParts = pathRegex.match(path);
  if (!pathParts) {
    return std::nullopt;
  }
  const std::string_view hostOrDrive = pathParts->group(path, 1);
  const auto [shareName, sharePath, shareNameAndPath] =
      extractShareNameAndPath(pathParts->group(path, 2));
  const std::string_view fullPath =
      path.substr(kPrefixLength, hostOrDrive.size() + shareNameAndPath.size());
  return detail::UncDetails{hostOrDrive, shareName, sharePath, shareNameAndPath, fullPath};
}

std::tuple<std::string_view, std::string_view, std::string_view>
UncUnnormalisedDeviceSharePath::extractShareNameAndPath(std::string_view shareNameAndPath) const {
  shareNameAndPath = uncUnnormalisedDevicePathHandler.withoutTrailingSlashes(shareNameAndPath);
  auto headAndTail = pathHeadAndTailRegex.match(shareNameAndPath);
  if (!headAndTail) {
    return {shareNameAndPath, {}, shareNameAndPath};
  }
  return {headAndTail->group(shareNameAndPath, 1), headAndTail->group(shareNameAndPath, 2),
          shareNameAndPath};
}

void UncUnnormalisedDeviceSharePath::validatePath(const std::string_view& windowsPath,
                                                  const detail::UncDetails& uncDetails) const {
  uncUnnormalisedDevicePathHandler.validatePath(windowsPath, uncDetails);

  if (uncDetails.hostOrDrive.empty()) {
    // E.g. `\\?\UNC\\path` - host segment is blank.
    throwError(kErrorInvalidHostname, windowsPath);
  }
  if (uncHostHandler.isInvalidHostname(uncDetails.hostOrDrive)) {
    throwError(kErrorInvalidHostname, windowsPath);
  }
}

void UncUnnormalisedDeviceSharePath::setUrlPath(const detail::UncDetails& uncDetails,
                                                ada::url& url) const {
  const Str urlPath = uncUnnormalisedDevicePathHandler.removeTrailingSlashesInPathSegments(
      uncDetails.shareNameAndPath);
  if (Str encodedUrlPath;
      detail::WindowsUrl::maybePercentEncodeAndAppendTo(urlPath, encodedUrlPath)) {
    GenericUrl::setUrlPath(encodedUrlPath, url);
  } else {
    GenericUrl::setUrlPath(urlPath, url);
  }
}
}  // namespace utils::path::windows::pathTypes
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
