// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#pragma once
#include <string_view>

#include <openassetio/export.h>

#include "./posix/detail.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Utilities for POSIX-specific URLs and paths.
 */
namespace utils::path::posix {
/**
 * POSIX path<->URL handler.
 *
 * This is the POSIX-specific entry point for converting a POSIX path
 * to/from a URL.
 */
struct FileUrlPathConverter {
  // NOLINTBEGIN(cppcoreguidelines-avoid-const-or-ref-data-members)
  detail::PosixUrl& urlHandler;
  detail::PosixPath& posixPathHandler;
  // NOLINTEND(cppcoreguidelines-avoid-const-or-ref-data-members)

  /**
   * Convert a POSIX path into a file URL.
   *
   * @param posixPath path to convert.
   * @return URL string.
   * @throws InputValidationException if the path is invalid (e.g.
   * relative) or unsupported.
   */
  [[nodiscard]] Str pathToUrl(const std::string_view& posixPath) const;

  /**
   * Convert a file URL to a POSIX path.
   *
   * @param url URL to convert.
   * @return POSIX path.
   * @throws InputValidationException if the URL or path that it decodes
   * to is invalid or unsupported.
   */
  [[nodiscard]] Str pathFromUrl(const std::string_view& url) const;
};
}  // namespace utils::path::posix
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
