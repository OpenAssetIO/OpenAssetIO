// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
#include <optional>
#include <string_view>

#include <ada.h>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

#include "../../Regex.hpp"
#include "../common.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Sundry utilities for POSIX-specific URLs and paths.
 */
namespace utils::path::posix::detail {

/**
 * Utility for POSIX paths.
 */
struct PosixPath {
  ForwardSlashSeparatedString& forwardSlashSeparatedStringHandler;

  Regex upwardsTraversalRegex{R"((^|/)\.\.(/|$))"};

  /**
   * Check if a path contains `..` segment.
   *
   * @param path Path to check.
   * @return true if a `..` segment was found, false otherwise.
   */
  [[nodiscard]] bool containsUpwardsTraversal(const std::string_view& str) const;

  /**
   * Check if a path starts with a `/`.
   *
   * @param path Path to check.
   * @return true if the path starts with `/`, false otherwise.
   */
  [[nodiscard]] static bool startsWithForwardSlash(const std::string_view& path);

  /**
   * Remove extraneous leading `/`s in a path.
   *
   * If there are exactly two leading `/`s, then they are left
   * unmodified, since the POSIX spec says:
   *
   * > A pathname that begins with two successive slashes may be
   *   interpreted in an implementation-defined manner, although more
   *   than two leading slashes shall be treated as a single slash.
   *
   * @param path Path to modify.
   * @return Updated path.
   */
  [[nodiscard]] Str removeTrailingForwardSlashesInPathSegments(const std::string_view& path) const;
};

/**
 * Utility for dealing with URLs pointing to POSIX paths.
 */
struct PosixUrl {
  Regex percentEncodedForwardSlashRegex{R"(%2F)"};
  /**
   * Augment default percent encoded set for paths.
   *
   * From swift-url's` `POSIXPathEncodeSet` docstring:
   *
   * - The '%' sign itself. Filesystem paths do not contain
   * percent-encoding, and any character sequences which look like
   * percent-encoding are just coincidences.
   * - Backslashes (`\`). They are allowed in POSIX paths and are not
   * separators.
   * - Colons (`:`) and vertical bars (`|`). These are sometimes
   * interpreted as Windows drive letter delimiters, which POSIX paths
   * obviously do not have.
   */
  static constexpr std::array kPercentEncodeCharacterSet = [] {
    constexpr std::uint8_t kByteSize = 8;
    constexpr std::size_t kArrSize = 32;  // 0xFF/kByteSize + 1;

    constexpr std::uint8_t kPercentHex = 0x25;
    constexpr std::uint8_t kBackSlashHex = 0x5C;
    constexpr std::uint8_t kColonHex = 0x3A;
    constexpr std::uint8_t kVerticalBarHex = 0x7C;

    std::array<uint8_t, kArrSize> charSet{};
    // Copy Ada's default %-encode set for URL path components.
    for (std::size_t idx = 0; idx < charSet.size(); ++idx) {
      charSet[idx] = ada::character_sets::PATH_PERCENT_ENCODE[idx];
    }
    // Augment the %-encode set with additional characters.
    for (std::uint8_t charCode : {kPercentHex, kBackSlashHex, kColonHex, kVerticalBarHex}) {
      charSet[charCode / kByteSize] |= static_cast<std::uint8_t>(1 << (charCode % kByteSize));
    }

    return charSet;
  }();

  /**
   * Check if a URL contains a percent-encoded `/`.
   *
   * @param url URL string to check.
   * @return true if a percent-encoded slash was found, false otherwise.
   */
  [[nodiscard]] bool containsPercentEncodedForwardSlash(const std::string_view& url) const;

  /**
   * Check if percent-encoding is needed for a URL path, and if so
   * update an output string.
   *
   * @param path Path to potentially percent-encode.
   * @param encodedPath String to update with result of
   * percent-encoding. Not modified if no encoding is needed.
   * @return true if encoding was required, false otherwise.
   */
  static std::optional<Str> maybePercentEncode(const std::string_view& path);
};
}  // namespace utils::path::posix::detail
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
