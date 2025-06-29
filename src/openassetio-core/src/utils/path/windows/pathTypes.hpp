// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once

#include <optional>
#include <string_view>
#include <tuple>

#include <ada.h>

#include <openassetio/export.h>

#include "../../Regex.hpp"
#include "./detail.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Handlers for the various top-level categories of Windows-specific
 * paths.
 */
namespace utils::path::windows::pathTypes {
/**
 * Utility for handling Windows drive paths e.g. `C:\path`.
 */
struct DrivePath {
  // NOLINTBEGIN(cppcoreguidelines-avoid-const-or-ref-data-members)
  detail::DriveLetter& driveLetterHandler;
  detail::NormalisedPath& normalisedPathHandler;
  // NOLINTEND(cppcoreguidelines-avoid-const-or-ref-data-members)

  static constexpr std::size_t kDriveLetterLength = 2;

  /**
   * Validate and convert a Windows drive path to a file URL.
   *
   * @param windowsPath Windows path to convert to a URL.
   * @param url URL object to update.
   */
  void toUrl(const std::string_view& windowsPath, ada::url& url) const;

  /**
   * Validate a Windows drive path.
   *
   * @param windowsPath Path to validate.
   */
  void validatePath(const std::string_view& windowsPath) const;

  /**
   * Set Windows path as path component of a file URL.
   *
   * The path is normalised according to Windows rules before being
   * percent encoded and set as the path component of the given URL
   * object.
   *
   * @param windowsPath Path to set as URL path component.
   * @param url URL object to update.
   */
  void setUrlPath(const std::string_view& windowsPath, ada::url& url) const;
};

/**
 * Utility for handling standard UNC share paths.
 *
 * I.e. `\\host\share`, but not `\\?\device\`
 *
 * These paths are normalised much like drive paths, e.g. `/` as well
 * as `\` is a path separator.
 */
struct UncSharePath {
  detail::UncHost& uncHostHandler;
  detail::NormalisedPath& normalisedPathHandler;
  detail::WindowsUrl& urlHandler;

  Regex pathRegex{R"(^([\\/]{2,})([^\\/]*)(.*)$)"};
  Regex pathHeadAndTailRegex{R"(^([\\/]+[^\\/]+)([\\/].*)$)"};

  /**
   * Validate and convert a Windows UNC share path to a file URL.
   *
   * No-op if the path is not a Windows UNC share path.
   *
   * Note that this will parse any UNC path, including device paths
   * `\\?\`, so these must be filtered out before calling this method.
   *
   * @param windowsPath Windows path to convert to a URL.
   * @param url URL object to update.
   * @return true if the path is a UNC share path, false otherwise.
   */
  bool toUrl(const std::string_view& windowsPath, ada::url& url) const;

  /**
   * Check if the path is a UNC path, and if so return a structure
   * containing useful features extracted from the path.
   *
   * Note that this will attempt to parse any UNC path, including `\\?\`
   * device paths, so these must be filtered out before this method is
   * called.
   *
   * @param path Path to parse.
   * @return Empty optional if the path is not a UNC path, otherwise
   * the results of parsing the path components.
   */
  [[nodiscard]] std::optional<detail::UncDetails> extractUncDetails(
      const std::string_view& path) const;

  /**
   * Normalise and split the share name and path components from a UNC
   * host path.
   *
   * Normalises the share path.
   *
   * @param shareNameAndPath UNC path excluding hostname prefix.
   * @return Share name, path and joined name and path, after
   * normalisation.
   */
  [[nodiscard]] std::tuple<std::string_view, std::string_view, std::string_view>
  extractShareNameAndPath(std::string_view shareNameAndPath) const;

  /**
   * Validate a Windows UNC share path.
   *
   * @param windowsPath Path to validate.
   * @param uncDetails UNC features of path.
   */
  void validatePath(const std::string_view& windowsPath,
                    const detail::UncDetails& uncDetails) const;

  /**
   * Set Windows UNC path as path component of a file URL.
   *
   * The UNC share path is normalised according to Windows rules before
   * being percent encoded and set as the path component of the given
   * URL object.
   *
   * @param windowsPath Path to set as URL path component.
   * @param url URL object to update.
   */
  void setUrlPath(const detail::UncDetails& uncDetails, ada::url& url) const;
};

/**
 * Utility for handling Windows device drive paths, i.e. `\\?\C:\`.
 *
 * The only Windows "devices" we support are drives (plus the special
 * "UNC" device that is handled by UncUnnormalisedDeviceSharePath).
 */
struct UncUnnormalisedDeviceDrivePath {
  detail::DriveLetter& driveLetterHandler;
  detail::UncUnnormalisedDevicePath& uncUnnormalisedDevicePathHandler;

  static constexpr std::string_view kPrefix = R"(\\?\)";
  Regex pathRegex{R"(^\\\\\?\\([^\\]*)(.*)$)"};

  /**
   * Validate and convert a Windows UNC device drive path to a file
   * URL.
   *
   * Note that this will parse all device paths, i.e. paths prefixed
   * with `\\?\`, including non-drive paths such as `\\?\UNC\`, so such
   * paths should be filtered before calling this method.
   *
   * No-op if the path is not a Windows device path.
   *
   * @param windowsPath Windows path to convert to a URL.
   * @param url URL object to update.
   * @return true if the path is a Windows UNC device path, false
   * otherwise.
   */
  bool toUrl(const std::string_view& windowsPath, ada::url& url) const;

  /**
   * Check if the path is a UNC device path, and if so return a
   * structure containing useful features extracted from the path.
   *
   * Assumes a device drive path, i.e. does not split out a share
   * name/path.
   *
   * @param path Path to parse.
   * @return Empty optional if the path is not a UNC device path,
   * otherwise the results of parsing the path components.
   */
  [[nodiscard]] std::optional<detail::UncDetails> extractUncDetails(
      const std::string_view& path) const;

  /**
   * Validate a Windows UNC device drive path.
   *
   * @param windowsPath Path to validate.
   * @param uncDetails UNC features of path.
   */
  void validatePath(const std::string_view& windowsPath,
                    const detail::UncDetails& uncDetails) const;

  /**
   * Set Windows UNC drive path as path component of a file URL.
   *
   * The path after the drive letter is percent encoded, if necessary.
   * Multiple trailing slashes in path segments are collapsed down to
   * one.
   *
   * @param windowsPath Path to set as URL path component.
   * @param url URL object to update.
   */
  void setUrlPath(const detail::UncDetails& uncDetails, ada::url& url) const;

  /**
   * Prefix a (normalised) drive path to make it an unnormalised device
   * path.
   *
   * E.g. `C:\path\to\file.ext` -> `\\?\C:\path\to\file.ext`
   *
   * Note: does not do any normalisation beforehand (e.g. converting
   * `/` to `\` etc).
   *
   * @param drivePath Path to prefix.
   * @return unnormalised device drive path.
   */
  static Str prefixDrivePath(std::string_view drivePath);
};

/**
 * Utility for handling Windows UNC device share paths, i.e. `\\?\UNC\`.
 */
struct UncUnnormalisedDeviceSharePath {
  detail::UncHost& uncHostHandler;
  detail::UncUnnormalisedDevicePath& uncUnnormalisedDevicePathHandler;
  detail::WindowsUrl& urlHandler;

  static constexpr std::string_view kPrefix = R"(\\?\UNC\)";
  Regex pathRegex{R"(^\\\\\?\\UNC\\([^\\]*)(.*)$)"};
  Regex pathHeadAndTailRegex{R"(^(\\[^\\]+)(.*)$)"};

  /**
   * Validate and convert a Windows UNC device share path to a file
   * URL.
   *
   * No-op if the path is not a Windows device share path.
   *
   * @param windowsPath Windows path to convert to a URL.
   * @param url URL object to update.
   * @return true if the path is a Windows UNC device share path, false
   * otherwise.
   */
  bool toUrl(const std::string_view& windowsPath, ada::url& url) const;

  /**
   * Check if the path is a UNC device share path, and if so return a
   * structure containing useful features extracted from the path.
   *
   * @param path Path to parse.
   * @return Empty optional if the path is not a UNC device share path,
   * otherwise the results of parsing the path components.
   */
  [[nodiscard]] std::optional<detail::UncDetails> extractUncDetails(
      const std::string_view& path) const;

  /**
   * Split the share name and path components from a UNC device share
   * path.
   *
   * Doesn't normalise the path, other than trimming extraneous
   * trailing `\`s.
   *
   * @param shareNameAndPath UNC device share path excluding hostname
   * prefix.
   * @return Share name, path and joined name and path, after
   * normalisation.
   */
  [[nodiscard]] std::tuple<std::string_view, std::string_view, std::string_view>
  extractShareNameAndPath(std::string_view shareNameAndPath) const;

  /**
   * Validate a Windows UNC device share path.
   *
   * @param windowsPath Path to validate.
   * @param uncDetails UNC features of path.
   */
  void validatePath(const std::string_view& windowsPath,
                    const detail::UncDetails& uncDetails) const;

  /**
   * Set Windows UNC device share path as path component of a file URL.
   *
   * Multiple trailing slashes in path segments are collapsed down to
   * one.
   *
   * @param uncDetails UNC features of path.
   * @param url URL object to update.
   */
  void setUrlPath(const detail::UncDetails& uncDetails, ada::url& url) const;

  /**
   * Prefix a (normalised) share path to make it an unnormalised device
   * path.
   *
   * E.g. `\\host\share\file.ext` -> `\\?\UNC\host\share\file.ext`
   *
   * Note: does not do any normalisation beforehand (e.g. converting
   * `/` to `\` etc).
   *
   * @param uncSharePath Path to prefix.
   * @return Unnormalised device share path.
   */
  static Str prefixUncSharePath(std::string_view uncSharePath);
};

}  // namespace utils::path::windows::pathTypes
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
