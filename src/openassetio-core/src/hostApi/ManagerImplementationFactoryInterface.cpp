// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

ManagerImplementationFactoryInterface::~ManagerImplementationFactoryInterface() = default;

ManagerImplementationFactoryInterface::ManagerImplementationFactoryInterface(
    log::LoggerInterfacePtr logger)
    : logger_{std::move(logger)} {}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
