// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <cstdlib>
#include <iostream>

#include <openassetio/log/SeverityFilter.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace log {
SeverityFilterPtr SeverityFilter::make(LoggerInterfacePtr upstreamLogger) {
  return std::shared_ptr<SeverityFilter>(new SeverityFilter(std::move(upstreamLogger)));
}

SeverityFilter::SeverityFilter(LoggerInterfacePtr upstreamLogger)
    : upstreamLogger_(std::move(upstreamLogger)) {
  /// @todo [#546] Redesign and improve env var handling and associated logging.

  // If the env var is set to a suitable int, attempt to extract a valid
  // severity from it, and use as minSeverity_.
  if (const char* envSeverityStr = std::getenv("OPENASSETIO_LOGGING_SEVERITY")) {
    const int envSeverity = std::atoi(envSeverityStr);
    const bool exactConversion = std::to_string(envSeverity) == envSeverityStr;
    if (!exactConversion || envSeverity < int(kDebugApi) || envSeverity > int(kCritical)) {
      std::string msg = "SeverityFilter: Invalid OPENASSETIO_LOGGING_SEVERITY value '";
      msg += envSeverityStr;
      msg += "' - ignoring.";
      upstreamLogger_->log(kError, msg);
    } else {
      minSeverity_ = static_cast<Severity>(envSeverity);
    }
  }
}

void SeverityFilter::log(Severity severity, const std::string& message) {
  if (severity < minSeverity_) {
    return;
  }
  upstreamLogger_->log(severity, message);
}

void SeverityFilter::setSeverity(LoggerInterface::Severity severity) { minSeverity_ = severity; }

LoggerInterface::Severity SeverityFilter::getSeverity() const { return minSeverity_; }

LoggerInterfacePtr SeverityFilter::upstreamLogger() const { return upstreamLogger_; }
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
