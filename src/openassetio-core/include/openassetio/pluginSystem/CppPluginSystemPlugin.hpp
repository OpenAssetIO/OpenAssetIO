// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

class OPENASSETIO_CORE_EXPORT CppPluginSystemPlugin {
 public:
  virtual ~CppPluginSystemPlugin() = default;
  [[nodiscard]] virtual openassetio::Str identifier() const = 0;
};
