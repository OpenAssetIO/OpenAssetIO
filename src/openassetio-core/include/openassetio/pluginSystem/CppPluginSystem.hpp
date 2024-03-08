// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once
#include <memory>
#include <string_view>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystem)

class OPENASSETIO_CORE_EXPORT CppPluginSystem {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystem)

  static Ptr make(log::LoggerInterfacePtr logger);

  void scan(std::string_view paths);

  [[nodiscard]] std::vector<openassetio::Str> identifiers() const;

 private:
  explicit CppPluginSystem(log::LoggerInterfacePtr logger);
  log::LoggerInterfacePtr logger_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
