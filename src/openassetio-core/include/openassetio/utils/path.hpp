// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#pragma once

#include <cstdint>
#include <memory>
#include <string_view>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {

/**
 * Indicator of platform type associate with a path.
 */
enum class PathType : std::uint8_t {
  /// Use the current system platform to determine path type.
  kSystem = 0,
  /// Assume a POSIX path.
  kPOSIX,
  /// Assume a Windows path (including UNC).
  kWindows
};

/**
 * Utility class for converting between file system paths and file URLs.
 *
 * The @ref PathType argument allows POSIX hosts to process paths/URLs
 * for Windows systems and vice versa.
 *
 * Construction of this class should not be considered cheap
 * (internally, multiple regex patterns are compiled). Once constructed,
 * an instance can be used to process any number of URLs/paths.
 *
 * Conversion of Windows UNC paths to file URLs is supported, including
 * `\\?\` device paths. Conversion of file URLs back to Windows
 * paths will prefer drive paths or standard UNC share paths, but will
 * promote to a device path if the path is longer than the Windows
 * MAX_PATH limit.
 *
 * Some corner cases that may be technically valid are not currently
 * supported, and will result in an exception if detected. E.g.
 *  - Upward traversals (`..`) as path segments - these may be a
 *    security risk.
 *  - Non-ASCII Windows server names.
 *  - Windows UNC non-normalised device paths (`\\?\`) that have
 *    forward-slashes within path segments.
 *  - Percent-encoded path separators.
 *  - Windows drive letters of the form `C|`.
 */
class OPENASSETIO_CORE_EXPORT FileUrlPathConverter {
 public:
  /// Constructor.
  FileUrlPathConverter();
  /// Defaulted destructor.
  ~FileUrlPathConverter();

  // Delete special member functions, for now, since copy/move needs
  // careful consideration of internals.

  /// Explicitly deleted copy constructor.
  FileUrlPathConverter(const FileUrlPathConverter &) = delete;
  /// Explicitly deleted move constructor.
  FileUrlPathConverter(FileUrlPathConverter &&) noexcept = delete;
  /// Explicitly deleted copy assignment.
  FileUrlPathConverter &operator=(const FileUrlPathConverter &) = delete;
  /// Explicitly deleted move assignment.
  FileUrlPathConverter &operator=(FileUrlPathConverter &&) noexcept = delete;

  /**
   * Construct a file URL from a path.
   *
   * The path must be absolute and not contain any upward traversals
   * (`..`) within it.
   *
   * Conversion of Windows UNC paths to file URLs is supported,
   * including standard `\\` shares, and `\\?\` drive and `\\?\\UNC\`
   * share device paths.
   *
   * Note that Windows device paths of the form `\\.\` are not
   * supported. This may be added in a future update.
   *
   * @param absolutePath Path string.
   *
   * @param pathType Platform associated with path.
   *
   * @return Converted file URL.
   *
   * @throws InputValidationException if the path is invalid or
   * unsupported.
   */
  [[nodiscard]] Str pathToUrl(std::string_view absolutePath,
                              PathType pathType = PathType::kSystem) const;

  /**
   * Construct a path from a file URL.
   *
   * Note that long Windows paths that exceed the Windows MAX_PATH limit
   * will be returned as a UNC device path (`\\?\C:\` or
   * `\\?\UNC\host\share`).
   *
   * @param fileUrl URL to convert.
   *
   * @param pathType Platform associated with path.
   *
   * @return Extracted path suitable for the @p pathType platform.
   *
   * @throws InputValidationException if the URL or path that it decodes
   * to is invalid or unsupported.
   */
  [[nodiscard]] Str pathFromUrl(std::string_view fileUrl,
                                PathType pathType = PathType::kSystem) const;

 private:
  std::unique_ptr<struct FileUrlPathConverterImpl> impl_;
};

}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
