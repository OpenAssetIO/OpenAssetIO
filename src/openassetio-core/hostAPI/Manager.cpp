// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostAPI/Manager.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostAPI {

Manager::Manager(managerAPI::ManagerInterfacePtr managerInterface)
    : managerInterface_{std::move(managerInterface)} {}

Str Manager::identifier() const { return managerInterface_->identifier(); }
Str Manager::displayName() const { return managerInterface_->displayName(); }
InfoDictionary Manager::info() const { return managerInterface_->info(); }

}  // namespace hostAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
