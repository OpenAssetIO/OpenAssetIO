// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

class OPENASSETIO_CORE_EXPORT CppPluginSystemManagerPlugin : public CppPluginSystemPlugin {
 public:
  [[nodiscard]] virtual managerApi::ManagerInterfacePtr interface() = 0;
};
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
