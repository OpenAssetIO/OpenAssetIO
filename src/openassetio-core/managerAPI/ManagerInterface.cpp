// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/managerAPI/ManagerInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace managerAPI {

ManagerInterface::ManagerInterface() = default;

InfoDictionary ManagerInterface::info() const { return {}; }

}  // namespace managerAPI
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
