// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/export.h>
#include <openassetio/enum.hpp>
#include <openassetio/typedefs.hpp>

#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
OPENASSETIO_DECLARE_PTR(LoggerInterface)
/**
 * An abstract base class that defines the receiving interface for
 * log messages generated a @ref manager or the API middleware.
 */
class OPENASSETIO_CORE_EXPORT LoggerInterface {
 public:
  /**
   * @name Log Severity
   * @{
   */
  enum Severity : EnumIdx { kDebugApi = 0, kDebug, kInfo, kProgress, kWarning, kError, kCritical };

  static constexpr EnumNames<7> kSeverityNames{"debugApi", "debug", "info",    "progress",
                                               "warning",  "error", "critical"};
  /// @}

  virtual ~LoggerInterface() = 0;

  /**
   * Logs a message to the user.
   *
   * This method must be implemented to present the supplied message
   * to the user in an appropriate fashion.
   *
   * @param message The message string to be logged.
   *
   * @param severity One of the severity constants defined in @ref
   * Severity.
   */
  virtual void log(Severity severity, const Str& message) = 0;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
