// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <array>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 This namespace contains code relevant to message logging within the
 API.

 @ref host "Host" authors provide an implementation of @ref
 LoggerInterface to a @ref manager to channel its messages. The API
 middleware also makes use of this logger to provide debugging
 information about use of the API at runtime.
*/
namespace log {
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
  enum Severity { kDebugApi = 0, kDebug, kInfo, kProgress, kWarning, kError, kCritical };

  static constexpr std::array kSeverityNames{"debugApi", "debug", "info",    "progress",
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
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
