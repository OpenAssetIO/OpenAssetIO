// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once
#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(pluginSystem, CppPluginSystemPlugin)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystem)

class OPENASSETIO_CORE_EXPORT CppPluginSystem {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystem)
  using PathAndPlugin = std::pair<std::filesystem::path, CppPluginSystemPluginPtr>;

  static Ptr make(log::LoggerInterfacePtr logger);

  void reset();

  void scan(std::string_view paths);

  [[nodiscard]] std::vector<std::string> identifiers() const;

  PathAndPlugin plugin(const openassetio::Identifier& identifier) const;

 private:
  using PluginMap = std::unordered_map<openassetio::Str, PathAndPlugin>;
  using MaybeIdentifierAndPlugin =
      std::optional<std::pair<openassetio::Identifier, CppPluginSystemPluginPtr>>;

  MaybeIdentifierAndPlugin maybeLoadPlugin(const std::filesystem::path& filePath);

  // Must be an exported function for gcc exception catching workaround.
  static void* openLibrary(const std::filesystem::path& filePath);

  explicit CppPluginSystem(log::LoggerInterfacePtr logger);
  log::LoggerInterfacePtr logger_;
  PluginMap plugins_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
