// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

HostPtr Host::make(hostApi::HostInterfacePtr hostInterface) {
  return std::shared_ptr<Host>(new Host(std::move(hostInterface)));
}

Host::Host(hostApi::HostInterfacePtr hostInterface) : hostInterface_{std::move(hostInterface)} {}

Identifier Host::identifier() const { return hostInterface_->identifier(); }
Str Host::displayName() const { return hostInterface_->displayName(); }
InfoDictionary Host::info() { return hostInterface_->info(); }

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
