// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <openassetio/pluginSystem/CppPluginSystemManagerImplementationFactory.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

CppPluginSystemManagerImplementationFactory::Ptr CppPluginSystemManagerImplementationFactory::make(
    const std::string_view paths, log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystemManagerImplementationFactory>(
      // Use (implicitly defined) move constructor to work around
      // private constructor being inaccessible by std::allocator.
      CppPluginSystemManagerImplementationFactory{paths, std::move(logger)});
}

CppPluginSystemManagerImplementationFactory::Ptr CppPluginSystemManagerImplementationFactory::make(
    log::LoggerInterfacePtr logger) {
  return Ptr{new CppPluginSystemManagerImplementationFactory{std::move(logger)}};
}

CppPluginSystemManagerImplementationFactory::CppPluginSystemManagerImplementationFactory(
    [[maybe_unused]] std::string_view paths, log::LoggerInterfacePtr logger)
    : ManagerImplementationFactoryInterface(std::move(logger)) {}

CppPluginSystemManagerImplementationFactory::CppPluginSystemManagerImplementationFactory(
    log::LoggerInterfacePtr logger)
    : ManagerImplementationFactoryInterface(std::move(logger)) {}

Identifiers CppPluginSystemManagerImplementationFactory::identifiers() {
  return openassetio::Identifiers();
}

managerApi::ManagerInterfacePtr CppPluginSystemManagerImplementationFactory::instantiate(
    [[maybe_unused]] const Identifier& identifier) {
  return openassetio::managerApi::ManagerInterfacePtr();
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
