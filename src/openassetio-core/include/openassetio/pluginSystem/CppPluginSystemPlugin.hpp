// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemPlugin)

class OPENASSETIO_CORE_EXPORT CppPluginSystemPlugin {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemPlugin)

  virtual ~CppPluginSystemPlugin();
  [[nodiscard]] virtual openassetio::Str identifier() const = 0;
};

using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)() noexcept;
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
