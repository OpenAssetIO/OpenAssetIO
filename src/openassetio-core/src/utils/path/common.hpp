// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once

#include <string_view>

#include <ada.h>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>
#include <openassetio/utils/path.hpp>

#include "../Regex.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Various utility components for handling different types of path/URL
 */
namespace utils::path {

// Non-`file://` URLs are invalid.
constexpr std::string_view kErrorNotAFileUrl = "Not a file URL";
// Path provided to pathToUrl is empty.
constexpr std::string_view kErrorEmptyPath = "Path is empty";
// E.g. empty path or no drive letter in Windows paths.
constexpr std::string_view kErrorInvalidPath = "Path is ill-formed";
// E.g. no leading / in path.
constexpr std::string_view kErrorRelativePath = "Path is relative";
// There's a `..` segment in the path.
constexpr std::string_view kErrorUpwardsTraversal = "Path contains upwards traversal";
// A `\0` was found in the (decoded) path.
constexpr std::string_view kErrorNullByte = "Path contains NULL bytes";
// Decoding a percent-encoded URL reveals an extra path separator.
constexpr std::string_view kErrorEncodedSeparator = "Percent-encoded path separator";
// E.g. Non-ASCII hostname in URL.
constexpr std::string_view kErrorUnsupportedHostname = "Unsupported hostname";
// E.g. Non-ASCII hostname in path.
constexpr std::string_view kErrorInvalidHostname = "Path references an invalid hostname";
// E.g. Windows device path with forward slashes - technically allowed
// (as a literal rather than path separator) but unsupported by us.
constexpr std::string_view kErrorUnsupportedDevicePath = "Unsupported Win32 device path";
// E.g. `file://server/path` on posix.
constexpr std::string_view kErrorNonLocal = "Unsupported non-local file";
// Ada flagged an error setting the path component of a URL.
constexpr std::string_view kErrorInvalidUrlPath = "Invalid URL path";
// Ada failed to parse a given URL.
constexpr std::string_view kErrorUrlParseFailure = "Invalid URL";

// Constants for common character (sets) used in string processing.
// Useful for grepability.
constexpr char kColon = ':';
constexpr char kPercent = '%';
constexpr char kHyphen = '-';
constexpr std::string_view kAnySlash = "\\/";
constexpr char kForwardSlash = '/';
constexpr char kBackSlash = '\\';
constexpr std::string_view kBackSlashStr = "\\";
constexpr std::string_view kDoubleBackSlash = R"(\\)";

/**
 * Throw an exception formatted to contain the problematic string.
 *
 * @param message Error message.
 * @param pathOrUrl Problematic string to append to message.
 */
void throwError(std::string_view message, std::string_view pathOrUrl);

/**
 * Utility for dealing with `/`-separated strings.
 *
 * I.e. posix paths and URLs.
 */
struct ForwardSlashSeparatedString {
  Regex trailingForwardSlashesInSegmentRegex{R"(//+)"};

  /**
   * Replace multiple `/`s between segments with a single `/`
   *
   * E.g. /path///file -> /path/file
   *
   * @param str Path or URL to process.
   * @return New string with `/`s collapsed.
   */
  [[nodiscard]] Str removeTrailingForwardSlashesInPathSegments(const std::string_view& str) const;
};

/**
 * Utility for non-platform specific paths.
 */
struct GenericPath {
#ifdef _WIN32
  static constexpr PathType kSystemPathType = PathType::kWindows;
#else
  static constexpr PathType kSystemPathType = PathType::kPOSIX;
#endif

  /**
   * Transform kSystemPath to the appropriate type for the running
   * system.
   *
   * @param pathType Input path type that might be kSystemPath.
   * @return Potentially transformed path type.
   */
  [[nodiscard]] static constexpr PathType resolveSystemPathType(PathType pathType) {
    return pathType == PathType::kSystem ? kSystemPathType : pathType;
  }

  /**
   * Check if a path contains a `\0` null byte.
   *
   * @param path Path to check.
   * @return true if a `\0` was found, false otherwise.
   */
  [[nodiscard]] static constexpr bool containsNullByte(std::string_view path) {
    return path.find_first_of('\0') != std::string_view::npos;
  }
};

/**
 * Utility for dealing with non-platform specific URLs.
 */
struct GenericUrl {
  Regex fileUrlRegex{R"(^file://)"};

  /**
   * Check if URL has a `file://` scheme.
   *
   * Regex (ab)used for case-insensitive matching.
   *
   * @param url URL to check.
   * @return true if URL has file scheme, false otherwise.
   */
  [[nodiscard]] bool isFileUrl(const std::string_view& url) const;

  /**
   * Set the path component on a URL object.
   *
   * @param urlPath Path to set.
   * @param url URL object to set path component on.
   * @throw InputValidationException If the path is invalid, according
   * to the Ada library.
   */
  static void setUrlPath(const Str& urlPath, ada::url& url);
};
}  // namespace utils::path
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
