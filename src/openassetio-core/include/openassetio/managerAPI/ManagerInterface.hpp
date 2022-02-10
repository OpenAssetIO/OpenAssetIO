// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#pragma once

#include <openassetio/export.h>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace managerAPI {

class OPENASSETIO_CORE_EXPORT ManagerInterface {
 public:
  ManagerInterface();
  ManagerInterface(ManagerInterface&& other) {}
};

}  // namespace managerAPI
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
