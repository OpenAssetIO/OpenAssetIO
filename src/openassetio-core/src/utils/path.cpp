// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include <openassetio/utils/path.hpp>

#include <openassetio/errors/exceptions.hpp>

#include "./path/common.hpp"
#include "./path/posix.hpp"
#include "./path/windows.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {
/**
 * Utility class for converting between file URLs and paths for both
 * Windows and POSIX systems.
 *
 * Reusable components (each usually consisting of a couple of
 * pre-compiled regexes and a handful of functions) are constructed and
 * dependency-injected bottom-up, resulting in top-level Windows and
 * POSIX handlers.
 *
 * We then delegate to the top-level Windows and POSIX utilities for the
 * bulk of path/URL processing.
 */
struct FileUrlPathConverterImpl {
  // Generic path/URL utilities.
  path::GenericUrl urlHandler{};
  path::ForwardSlashSeparatedString forwardSlashSeparatedStringHandler{};

  // Common Windows path/URL utilities.
  path::windows::detail::WindowsUrl windowsUrlHandler{};
  path::windows::detail::UncHost uncHostHandler{};
  path::windows::detail::DriveLetter driveLetterHandler{};
  path::windows::detail::NormalisedPath windowsNormalisedPathHandler{};
  path::windows::detail::UncUnnormalisedDevicePath uncUnnormalisedDevicePathHandler{};

  // Windows path utilities for specific types of path.
  path::windows::pathTypes::DrivePath drivePathHandler{driveLetterHandler,
                                                       windowsNormalisedPathHandler};
  path::windows::pathTypes::UncSharePath uncSharePathHandler{
      uncHostHandler, windowsNormalisedPathHandler, windowsUrlHandler};
  path::windows::pathTypes::UncUnnormalisedDeviceSharePath uncUnnormalisedDeviceSharePathHandler{
      uncHostHandler, uncUnnormalisedDevicePathHandler, windowsUrlHandler};
  path::windows::pathTypes::UncUnnormalisedDeviceDrivePath uncUnnormalisedDeviceDrivePathHandler{
      driveLetterHandler, uncUnnormalisedDevicePathHandler};

  // Entry point for converting Windows path<->URL.
  path::windows::FileUrlPathConverter windowsFileUrlPathConverter{
      windowsUrlHandler,
      driveLetterHandler,
      uncHostHandler,
      forwardSlashSeparatedStringHandler,
      drivePathHandler,
      uncSharePathHandler,
      uncUnnormalisedDeviceDrivePathHandler,
      uncUnnormalisedDeviceSharePathHandler};

  // POSIX path/URL utilities.
  path::posix::detail::PosixPath posixPathHandler{forwardSlashSeparatedStringHandler};
  path::posix::detail::PosixUrl posixUrlHandler{};

  // Entry point for converting POSIX path<->URL.
  path::posix::FileUrlPathConverter posixFileUrlPathConverter{posixUrlHandler, posixPathHandler};

  /**
   * Validate a path and construct a file URL from it.
   *
   * @param path Path string.
   * @param pathType Platform associated with path.
   * @return Converted file URL.
   * @throws InputValidationException if the path is invalid or
   * unsupported.
   */
  [[nodiscard]] Str pathToUrl(const std::string_view path, PathType pathType) const {
    if (path.empty()) {
      throw errors::InputValidationException(Str{path::kErrorEmptyPath});
    }

    if (path::GenericPath::containsNullByte(path)) {
      throw errors::InputValidationException(Str{path::kErrorNullByte});
    }

    pathType = path::GenericPath::resolveSystemPathType(pathType);

    return pathType == PathType::kWindows ? windowsFileUrlPathConverter.pathToUrl(path)
                                          : posixFileUrlPathConverter.pathToUrl(path);
  }

  /**
   * Convert a file URL to a path for a given platform type.
   *
   * @param fileUrl URL to convert.
   * @param pathType Platform associated with path.
   * @return Platform-specific path string.
   * @throws InputValidationException if the URL or path that it decodes
   * to is invalid or unsupported.
   */
  [[nodiscard]] Str pathFromUrl(const std::string_view fileUrl, PathType pathType) const {
    if (!urlHandler.isFileUrl(fileUrl)) {
      path::throwError(path::kErrorNotAFileUrl, fileUrl);
    }
    pathType = path::GenericPath::resolveSystemPathType(pathType);
    return pathType == PathType::kWindows ? windowsFileUrlPathConverter.pathFromUrl(fileUrl)
                                          : posixFileUrlPathConverter.pathFromUrl(fileUrl);
  }
};

FileUrlPathConverter::FileUrlPathConverter()
    : impl_{std::make_unique<FileUrlPathConverterImpl>()} {}

FileUrlPathConverter::~FileUrlPathConverter() = default;

Str FileUrlPathConverter::pathToUrl(std::string_view absolutePath, PathType pathType) const {
  return impl_->pathToUrl(absolutePath, pathType);
}

Str FileUrlPathConverter::pathFromUrl(std::string_view fileUrl, PathType pathType) const {
  return impl_->pathFromUrl(fileUrl, pathType);
}
}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
