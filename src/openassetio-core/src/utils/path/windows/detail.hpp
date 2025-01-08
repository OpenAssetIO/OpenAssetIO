// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

#include <ada.h>

#include <openassetio/export.h>

#include "../../Regex.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Sundry utilities for Windows-specific URLs and paths.
 */
namespace utils::path::windows::detail {
/**
 * Utility for dealing with URLs pointing to Windows paths.
 */
struct WindowsUrl {
  static constexpr std::string_view kLocalHostIP = "127.0.0.1";
  static constexpr std::string_view kIp6HostSuffix = ".ipv6-literal.net";
  Regex ip6HostRegex{R"(^\[([A-Z0-9:]+)\]$)"};
  Regex localHostRegex{"^localhost$"};
  Regex percentEncodedSlashRegex{R"(%(:?5C|2F))"};
  /**
   * Augment default percent encoded set for paths.
   *
   * From swift-url's` `WindowsPathEncodeSet` docstring:
   *
   * - The '%' sign itself. Filesystem paths do not contain
   * percent-encoding, and any character sequences which look like
   * percent-encoding are just coincidences.
   * - Note that the colon character (`:`) is also included, so this
   * encode-set is not appropriate for Windows drive letter components.
   * Drive letters should not be percent-encoded.
   */
  static constexpr std::array kPercentEncodeCharacterSet = [] {
    constexpr std::uint8_t kByteSize = 8;
    constexpr std::size_t kArrSize = 32;  // 0xFF/kByteSize + 1;

    constexpr std::uint8_t kPercentHex = 0x25;
    constexpr std::uint8_t kColonHex = 0x3A;
    constexpr std::uint8_t kVerticalBarHex = 0x7C;

    std::array<uint8_t, kArrSize> charSet{};
    // Copy Ada's default %-encode set for URL path components.
    for (std::size_t idx = 0; idx < charSet.size(); ++idx) {
      charSet[idx] = ada::character_sets::PATH_PERCENT_ENCODE[idx];
    }
    // Augment the %-encode set with additional characters.
    for (const std::uint8_t charCode : {kPercentHex, kColonHex, kVerticalBarHex}) {
      charSet[charCode / kByteSize] |= static_cast<std::uint8_t>(1 << (charCode % kByteSize));
    }

    return charSet;
  }();

  /**
   * Check if a URL contains a percent-encoded `\` or `/`.
   *
   * @param url URL string to check.
   * @return true if a percent-encoded slash was found, false otherwise.
   */
  [[nodiscard]] bool containsPercentEncodedSlash(const std::string_view& url) const;

  /**
   * Detect an IP6 address, and if found convert it to a valid UNC
   * hostname.
   *
   * @param host hostname that is potentially an IP6 address.
   * @return Unset optional if hostname is not an IP6 address, otherwise
   * a valid UNC hostname pointing to the IP6 address.
   */
  [[nodiscard]] std::optional<Str> ip6ToValidHostname(const std::string_view& host) const;

  /**
   * Check if percent-encoding is needed for a URL path, and if so
   * append the encoded string to a second string.
   *
   * @param path Path to potentially percent-encode.
   * @param appendTo String to append result of percent-encoding. Not
   * modified if no encoding is needed.
   * @return true if encoding was required, false otherwise.
   */
  static bool maybePercentEncodeAndAppendTo(const std::string_view& path, Str& appendTo);

  /**
   * Set the host part on a URL object.
   *
   * Converts localhost to 127.0.0.1, to avoid the possibility that
   * `file://localhost/` would be auto collapsed to `file:///` during
   * transport, which would not then be valid when converting back to a
   * path on Windows.
   *
   * @param host Hostname to set on URL object.
   * @param url URL object o modify
   * @return true if setting host succeeded, false if the host is
   * invalid, according to the Ada library.
   */
  bool setUrlHost(const std::string_view& host, ada::url& url) const;
};

/**
 * Parsed details of a UNC (i.e. `\\`-prefixed) path.
 */
struct UncDetails {
  /// Hostname or drive letter.
  std::string_view hostOrDrive;
  /// Host share name (blank for UNC device drive paths).
  std::string_view shareName;
  /// Path in share - i.e. everything after the share name.
  std::string_view sharePath;
  /// Combined share name and path - i.e. everything after the
  /// host/drive.
  std::string_view shareNameAndPath;
  /// Complete path excluding UNC prefix - i.e. host + share name and
  /// path
  std::string_view fullPath;
};

/**
 * Utility for handling Windows drive and standard UNC share paths.
 *
 * I.e. `C:\` and `\\` but NOT `\\?\`.
 *
 * These paths have various normalisation rules, e.g. treating `/` as
 * well as `\` as a path separator, and trimming some trailing chars
 * from path segments.
 *
 * See https://learn.microsoft.com/en-us/dotnet/standard/io/file-path-formats
 */
struct NormalisedPath {
  Regex upwardsTraversalRegex{R"((^|[\\/])\.\.([\\/]|$))"};
  Regex trailingDotsAsFileRegex{R"([\\/](\.{3,})$)"};
  Regex trailingDotsInFileRegex{R"([^.\\/](\.+)$)"};
  Regex trailingDotsAndSpacesRegex{R"([\\/][^\\/ ]*( [. ]*)$)"};
  Regex trailingSlashesRegex{R"([\\/]([\\/]+)$)"};
  Regex trailingSingleDotInSegmentRegex{R"((?<![.\\/])\.(?=[/\\]))"};
  Regex trailingSlashesInSegmentRegex{R"([\\/][\\/]+)"};

  /**
   * Get a view of the input path with all but the last trailing slash
   * removed.
   *
   * E.g. `C:\some\\\path\\\\ -> `C:\some\\\path\`
   *
   * @param path Path to (potentially) trim.
   * @return Input path if no trimming was needed, otherwise a
   * substring view with extraneous trailing slashes trimmed.
   */
  [[nodiscard]] std::string_view withoutTrailingSlashes(const std::string_view& path) const;

  /**
   * If the final segment of input path ends in three or more `.`s, get
   * a view of the input path with these removed.
   *
   * E.g. `C:\some\path\....` -> `C:\some\path\`
   *
   * Does not affect single `.` or double `..`. Double dots are
   * disallowed (see kErrorUpwardsTraversal). Single dots are collapsed
   * for us by the Ada URL library's own normalisation.
   *
   * @param path Path to (potentially) trim.
   * @return Input path if no trimming was needed, otherwise a
   * substring view with extraneous trailing dots trimmed.
   */
  [[nodiscard]] std::string_view withoutTrailingDotsAsFile(const std::string_view& path) const;

  /**
   * If the final segment of the input path is a file name, and the file
   * name ends in one or more `.`s, trim them.
   *
   * Also see @ref removeTrailingDotsInPathSegments.
   *
   * E.g. `C:\some\file...` -> `C:\some\file`
   *
   * @param path Path to (potentially)trim
   * @return Input path if no trimming was needed, otherwise a
   * substring view with extraneous trailing dots trimmed.
   */
  [[nodiscard]] std::string_view withoutTrailingDotsInFile(const std::string_view& path) const;

  /**
   * If the final segment of the input path ends in a space followed by
   * any number of spaces and dots, remove them.
   *
   * E.g. `C:\some\file ... .. .` -> `C:\some\file`
   *
   * @param path Path to (potentially)trim
   * @return Input path if no trimming was needed, otherwise a
   * substring view with extraneous trailing dots trimmed.
   */
  [[nodiscard]] std::string_view withoutTrailingSpacesAndDots(const std::string_view& path) const;

  /**
   * Check if a path contains `..` segment.
   *
   * @param path Path to check.
   * @return True if a `..` segment was found, false otherwise.
   */
  [[nodiscard]] bool containsUpwardsTraversal(const std::string_view& path) const;

  /**
   * Remove all trailing `.`s in each path segment.
   *
   * E.g. `C:\path...\to.\file` -> `C:\path\to\file`
   *
   * @param path Path to process.
   * @return New string with any trailing dots within segments removed.
   */
  [[nodiscard]] Str removeTrailingDotsInPathSegments(const std::string_view& path) const;

  /**
   * Remove all trailing slashes in each path segment.
   *
   * E.g. `C:\path\/\/to\\file` -> `C:\path\to\file`
   *
   * @param path Path to process.
   * @return New string with any trailing slashes within segments
   * removed.
   */
  [[nodiscard]] Str removeTrailingSlashesInPathSegments(const std::string_view& path) const;

  /**
   * Check if given path starts with a path separator.
   *
   * E.g. `/some/path` or `\some/path`, but not `some/path`.
   *
   * @param path Path to check.
   * @return true if the path starts with a separator, false otherwise.
   */
  [[nodiscard]] static bool startsWithSlash(const std::string_view& path);
};

/**
 * Utility for handling Windows drive letters e.g. `C:\`.
 */
struct DriveLetter {
  Regex driveRegex{R"(^[A-Z]:$)"};
  Regex absoluteDrivePathRegex{R"(^[A-Z]:[/\\])"};
  /**
   * Check if a given string is a Windows drive letter.
   *
   * E.g. `C:`, but not `C:\` - i.e. just the drive letter matches.
   *
   * @param str String to check.
   * @return true if string is a drive letter, false otherwise.
   */
  [[nodiscard]] bool isDrive(const std::string_view& str) const;

  /**
   * Check if a given string is a Windows absolute path on a drive.
   *
   * E.g. `C:\path` or `C:\`, but not `C:` or `hostname`.
   *
   * @param str String to check.
   * @return true if string is an absolute drive path, false otherwise.
   */
  [[nodiscard]] bool isAbsoluteDrivePath(const std::string_view& str) const;
};

/**
 * Utility handler for UNC path host component.
 *
 * I.e. the "host" in `\\host\share\path`.
 */
struct UncHost {
  /**
   * Invalid UNC hostname regex.
   *
   * - Unicode domains are unsupported, so ensure ASCII.
   * - Ensure no %-encoding.
   * - Reject "?" and "." as UNC hostnames. From swift-url code comments:
   *   > Otherwise we might create something which looks like a Win32 file
   *     namespace/local device path
   * - Reject drive letters as hostnames.
   */
  Regex invalidHostnameRegex{R"(^[.?]$|[^[:ascii:]]|%|^[A-Z]:$)"};

  /**
   * Check if a given hostname is invalid.
   *
   * @param host Hostname to check.
   * @return true if the hostname is invalid, false otherwise.
   */
  [[nodiscard]] bool isInvalidHostname(const std::string_view& host) const;
};

/**
 * Utility handler for non-normalised UNC device paths, i.e. `\\?\`.
 *
 * These path types do not undergo normalisation and so e.g. only
 * support `\` as a separator.
 *
 * The only normalisation we do is to collapse multiple `\` down to
 * one.
 */
struct UncUnnormalisedDevicePath {
  Regex upwardsTraversalRegex{R"((^|\\)\.\.(\\|$))"};
  Regex trailingSlashesRegex{R"(\\(\\+)$)"};
  Regex trailingSlashesInSegmentRegex{R"((\\\\+))"};

  /**
   * Validate a Windows UNC device path.
   *
   * @param windowsPath Path to validate.
   * @param uncDetails UNC features of path.
   */
  void validatePath(const std::string_view& windowsPath, const UncDetails& uncDetails) const;

  /**
   * Trim trailing `\`s from a path.
   *
   * E.g. `\\?\C:\directory\\\\\` -> `\\?\C:\directory\`
   *
   * @param path Path to trim.,
   * @return Input path if there was nothing to trim, otherwise a
   * substring view of the path with extraneous `\`s removed.
   */
  [[nodiscard]] std::string_view withoutTrailingSlashes(const std::string_view& path) const;

  /**
   * Check if a path contains a `/` anywhere.
   *
   * @param path Path to check.
   * @return true if a `/` was found, false otherwise.
   */
  [[nodiscard]] static bool containsForwardSlash(const std::string_view& path);

  /**
   * Check if a path contains `..` segment.
   *
   * @param path Path to check.
   * @return true if a `..` segment was found, false otherwise.
   */
  [[nodiscard]] bool containsUpwardsTraversal(const std::string_view& str) const;

  /**
   * Remove all trailing slashes in each path segment.
   *
   * E.g. `\\?\C:\path\\\\to\\file` -> `\\?\C:\path\to\file`
   *
   * @param path Path to process.
   * @return New string with any trailing slashes within segments
   * removed.
   */
  [[nodiscard]] Str removeTrailingSlashesInPathSegments(const std::string_view& path) const;
};

}  // namespace utils::path::windows::detail
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
