// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface);

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {
class OPENASSETIO_CORE_EXPORT CppPluginSystem {
 public:
  explicit CppPluginSystem(log::LoggerInterfacePtr logger);

 private:
  log::LoggerInterfacePtr logger_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
