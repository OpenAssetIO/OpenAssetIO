// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/export.h>
#include <openassetio/ui/pluginSystem/CppPluginSystemUIDelegatePlugin.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::pluginSystem {
// Define destructor in .cpp to avoid undefined reference errors when
// dynamic loading on Windows.
CppPluginSystemUIDelegatePlugin::~CppPluginSystemUIDelegatePlugin() = default;
}  // namespace ui::pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
