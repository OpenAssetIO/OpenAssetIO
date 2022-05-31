// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/managerAPI/HostSession.hpp>

#include <openassetio/managerAPI/Host.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerAPI {

HostSession::HostSession(HostPtr host) : host_{std::move(host)} {}

HostPtr HostSession::host() const { return host_; }

}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
