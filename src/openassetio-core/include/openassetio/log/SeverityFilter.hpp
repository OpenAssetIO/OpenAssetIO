// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd

#include <openassetio/export.h>
#include <openassetio/log/LoggerInterface.hpp>

#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace log {
OPENASSETIO_DECLARE_PTR(SeverityFilter)
/**
 * The SeverityFilter is a wrapper for a logger that drops messages
 * below a requested severity. More severe messages are relayed.
 *
 * @envvar **OPENASSETIO_LOGGING_SEVERITY** *[int]* If set, the default
 * displaySeverity for the filter is set to the value of the env var.
 */
class OPENASSETIO_CORE_EXPORT SeverityFilter final : public LoggerInterface {
 public:
  /**
   * Creates a new instance of the SeverityFilter
   *
   * The filter defaults to the @ref Severity.kWarning "kWarning"
   * severity.
   *
   * @param upstreamLogger A logger that will receive messages of the
   * requested severity or above.
   *
   * @see @fqref{log.LoggerInterface.Severity} "LoggerInterface.Severity"
   */
  [[nodiscard]] SeverityFilterPtr static make(LoggerInterfacePtr upstreamLogger);

  /**
   * Returns the logger wrapped by the filter.
   */
  [[nodiscard]] LoggerInterfacePtr upstreamLogger() const;

  /**
   * @name Filter Severity
   * Messages logged with a severity greater or equal to this will be displayed.
   * @{
   */

  /**
   * Sets the minimum severity of message that will be passed on to the
   * @ref upstreamLogger.
   *
   * @param severity The minimum severity.
   *
   * @see @fqref{log.LoggerInterface.Severity} "LoggerInterface.Severity"
   */
  void setSeverity(LoggerInterface::Severity severity);

  /**
   * Returns the minimum severity of message that will be passed on to the
   * @ref upstreamLogger.
   *
   * @see @fqref{log.LoggerInterface.Severity} "LoggerInterface.Severity"
   */
  [[nodiscard]] LoggerInterface::Severity getSeverity() const;

  /**
   * @}
   */

  void log(Severity severity, const Str& message) override;

 private:
  explicit SeverityFilter(LoggerInterfacePtr upstreamLogger);

  Severity minSeverity_ = Severity::kWarning;
  LoggerInterfacePtr upstreamLogger_;
};
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
