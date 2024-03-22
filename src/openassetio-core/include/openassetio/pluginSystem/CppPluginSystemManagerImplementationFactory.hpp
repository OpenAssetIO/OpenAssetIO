// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
#include <filesystem>

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(pluginSystem, CppPluginSystemManagerPlugin)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemManagerImplementationFactory)

class OPENASSETIO_CORE_EXPORT CppPluginSystemManagerImplementationFactory
    : public hostApi::ManagerImplementationFactoryInterface {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemManagerImplementationFactory)

  static constexpr std::string_view kPluginEnvVar = "OPENASSETIO_PLUGIN_PATH";

  static Ptr make(log::LoggerInterfacePtr logger);
  static Ptr make(openassetio::Str paths, log::LoggerInterfacePtr logger);

  using hostApi::ManagerImplementationFactoryInterface::ManagerImplementationFactoryInterface;
  Identifiers identifiers() override;
  managerApi::ManagerInterfacePtr instantiate(const Identifier& identifier) override;

 private:
  explicit CppPluginSystemManagerImplementationFactory(log::LoggerInterfacePtr logger);
  CppPluginSystemManagerImplementationFactory(openassetio::Str paths,
                                              log::LoggerInterfacePtr logger);

  using ManagerPluginMap =
      std::unordered_map<openassetio::Str,
                         std::pair<std::filesystem::path, CppPluginSystemManagerPluginPtr>>;

  openassetio::Str paths_;
  ManagerPluginMap plugins_;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
