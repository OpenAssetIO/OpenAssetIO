// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {
CppPluginSystem::CppPluginSystem(log::LoggerInterfacePtr logger) : logger_{std::move(logger)} {}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
