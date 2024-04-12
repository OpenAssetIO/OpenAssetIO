// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <openassetio/pluginSystem/CppPluginSystemManagerPlugin.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {
// Define destructor in .cpp to avoid undefined reference errors when
// dynamic loading on Windows.
CppPluginSystemManagerPlugin::~CppPluginSystemManagerPlugin() = default;
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
