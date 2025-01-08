// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <array>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <memory>

#include <openassetio/export.h>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/typedefs.hpp>

// Foreground ANSI color codes (combined with \033[<color>m)
constexpr std::array kSeverityColors = {36, 32, 32, 0, 33, 31, 31};
constexpr int kSeverityWidth = 11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace log {
ConsoleLoggerPtr ConsoleLogger::make(bool shouldColorOutput) {
  return std::shared_ptr<ConsoleLogger>(new ConsoleLogger(shouldColorOutput));
}

ConsoleLogger::ConsoleLogger(bool shouldColorOutput) : shouldColorOutput_(shouldColorOutput) {}

void ConsoleLogger::log(Severity severity, const Str& message) {
  auto severityIdx = static_cast<std::size_t>(severity);

  if (shouldColorOutput_) {
    std::cerr << "\033[0;" << kSeverityColors[severityIdx] << "m";
  }

  // NOLINTNEXTLINE(readability-magic-numbers)
  std::cerr << std::setw(kSeverityWidth) << kSeverityNames[severityIdx] << ": " << message;

  if (shouldColorOutput_) {
    std::cerr << "\033[0m";
  }

  std::cerr << "\n";
}
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
