// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)

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
  static Ptr make(std::string_view paths, log::LoggerInterfacePtr logger);

  using hostApi::ManagerImplementationFactoryInterface::ManagerImplementationFactoryInterface;
  Identifiers identifiers() override;
  managerApi::ManagerInterfacePtr instantiate(const Identifier& identifier) override;

 private:
  explicit CppPluginSystemManagerImplementationFactory(log::LoggerInterfacePtr logger);
  CppPluginSystemManagerImplementationFactory(std::string_view paths,
                                              log::LoggerInterfacePtr logger);
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
