// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/managerApi/HostSession.hpp>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

HostSessionPtr HostSession::make(HostPtr host, log::LoggerInterfacePtr logger) {
  return std::shared_ptr<HostSession>(new HostSession(std::move(host), std::move(logger)));
}

HostSession::HostSession(HostPtr host, log::LoggerInterfacePtr logger)
    : host_{std::move(host)}, logger_{std::move(logger)} {}

HostPtr HostSession::host() const { return host_; }
const log::LoggerInterfacePtr& HostSession::logger() const { return logger_; }

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
