// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/managerApi/HostSession.hpp>

#include <openassetio/managerApi/Host.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

HostSessionPtr HostSession::make(HostPtr host) {
  return std::shared_ptr<HostSession>(new HostSession(std::move(host)));
}

HostSession::HostSession(HostPtr host) : host_{std::move(host)} {}

HostPtr HostSession::host() const { return host_; }

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
