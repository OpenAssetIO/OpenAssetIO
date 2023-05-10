// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd

#include <openassetio/export.h>
#include <openassetio/log/LoggerInterface.hpp>

#pragma once
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace log {
OPENASSETIO_DECLARE_PTR(ConsoleLogger)
/**
 * A logger that sends messages to the console (stderr).
 */
class OPENASSETIO_CORE_EXPORT ConsoleLogger final : public LoggerInterface {
 public:
  OPENASSETIO_ALIAS_PTR(ConsoleLogger)

  /**
   * Creates a new instance of the ConsoleLogger
   *
   * @param shouldColorOutput When true, messages will be colored based on
   * their severity.
   */
  [[nodiscard]] ConsoleLoggerPtr static make(bool shouldColorOutput = true);

  /**
   */
  void log(Severity severity, const Str& message) override;

 private:
  explicit ConsoleLogger(bool shouldColorOutput);

  bool shouldColorOutput_;
};
}  // namespace log
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
