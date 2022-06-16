// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/managerAPI/ManagerInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerAPI {

ManagerInterface::ManagerInterface() = default;

InfoDictionary ManagerInterface::info() const { return {}; }

ManagerStateBasePtr ManagerInterface::createState(
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  return nullptr;
}

ManagerStateBasePtr ManagerInterface::createChildState(
    [[maybe_unused]] const ManagerStateBasePtr& parentState,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "createChildState called on a manager that does not implement a custom state.");
}

std::string ManagerInterface::persistenceTokenForState(
    [[maybe_unused]] const ManagerStateBasePtr& state,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "persistenceTokenForState called on a manager that does not implement a custom state.");
}

ManagerStateBasePtr ManagerInterface::stateFromPersistenceToken(
    [[maybe_unused]] const std::string& token,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "stateFromPersistenceToken called on a manager that does not implement a custom state.");
}

}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
