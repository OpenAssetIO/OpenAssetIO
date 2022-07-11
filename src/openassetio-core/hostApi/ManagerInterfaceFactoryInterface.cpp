// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/ManagerInterfaceFactoryInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

ManagerInterfaceFactoryInterface::~ManagerInterfaceFactoryInterface() = default;

ManagerInterfaceFactoryInterface::ManagerInterfaceFactoryInterface(LoggerInterfacePtr logger)
    : logger_{std::move(logger)} {}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
