// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <utility>

#include <openassetio/export.h>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

ManagerImplementationFactoryInterface::~ManagerImplementationFactoryInterface() = default;

ManagerImplementationFactoryInterface::ManagerImplementationFactoryInterface(
    log::LoggerInterfacePtr logger)
    : logger_{std::move(logger)} {}

const log::LoggerInterfacePtr& ManagerImplementationFactoryInterface::logger() const {
  return logger_;
}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
