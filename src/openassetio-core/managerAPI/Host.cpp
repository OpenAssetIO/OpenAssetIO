// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostAPI/HostInterface.hpp>
#include <openassetio/managerAPI/Host.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerAPI {

Host::Host(hostAPI::HostInterfacePtr hostInterface) : hostInterface_{std::move(hostInterface)} {}

Str Host::identifier() const { return hostInterface_->identifier(); }
Str Host::displayName() const { return hostInterface_->displayName(); }
InfoDictionary Host::info() const { return hostInterface_->info(); }

}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
