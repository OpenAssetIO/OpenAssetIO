// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#pragma once

#include <array>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

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
 *
 * @note OpenAssetIO makes use of shared pointers to facilitate object
 * lifetime management across multiple languages. Instances passed into
 * API methods via shared pointer may have their lifetimes extended
 * beyond that of your code.
 */
// NOLINTNEXTLINE(cppcoreguidelines-special-member-functions)
class OPENASSETIO_CORE_EXPORT LoggerInterface {
 public:
  OPENASSETIO_ALIAS_PTR(LoggerInterface)

  /**
   * @name Log Severity
   * @{
   */
  // NOLINTNEXTLINE(performance-enum-size): requires binary breaking change
  enum class Severity { kDebugApi, kDebug, kInfo, kProgress, kWarning, kError, kCritical };

  static constexpr std::array kSeverityNames{"debugApi", "debug", "info",    "progress",
                                             "warning",  "error", "critical"};
  /// @}

  /// Defaulted polymorphic destructor.
  virtual ~LoggerInterface();

  /**
   * Logs a message to the user.
   *
   * This method must be implemented to present the supplied message
   * to the user in an appropriate fashion.
   *
   * @param severity One of the severity constants defined in @ref
   * Severity.
   *
   * @param message The message string to be logged.
   */
  virtual void log(Severity severity, const Str& message) = 0;

  /**
   * Check if a given severity level should/will be filtered out.
   *
   * The implementation of the logger may have a mechanism by which
   * certain severity levels are not output. If a severity level is not
   * output, then constructing a string to pass to the logger is wasted
   * effort. This method can be queried before constructing a complex
   * string, in order to avoid that wasted effort.
   *
   * Implementors of LoggerInterface subclasses should override this
   * method if they wish to conditionally skip logging at particular
   * severity levels.
   *
   * If @ref log is called regardless, with a severity that elicits a
   * `false` response from this method, then the logger may still output
   * the message, but it is not guaranteed (and is discouraged).
   *
   * The default implementation returns `true` for all severities.
   *
   * @param severity Severity level to check.
   *
   * @return Whether a message will be output if `log` is called
   * with the given severity.
   */
  [[nodiscard]] virtual bool isSeverityLogged(Severity severity) const;

  /**
   * @name Conveniences
   * @{
   *
   * Conveniences, equivalent to calling @ref LoggerInterface.log "log"
   * with the corresponding @ref Severity.
   */

  void debugApi(const Str& message);
  void debug(const Str& message);
  void info(const Str& message);
  void progress(const Str& message);
  void warning(const Str& message);
  void error(const Str& message);
  void critical(const Str& message);

  /**
   * @}
   */
};
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
