// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once
#include <openassetio/export.h>
#include <openassetio/python/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(hostApi, ManagerImplementationFactoryInterface)
OPENASSETIO_FWD_DECLARE(log, LoggerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Utilities for bridging from C++ to Python.
 */
namespace python {  // NOLINT(modernize-concat-nested-namespaces)
/// Host-side utilities for bridging from C++ to Python.
namespace hostApi {
/**
 * Retrieve an instance of the Python manager plugin system
 * implementation.
 *
 * @return Python plugin system.
 */
OPENASSETIO_PYTHON_BRIDGE_EXPORT openassetio::hostApi::ManagerImplementationFactoryInterfacePtr
createPythonPluginSystemManagerImplementationFactory(log::LoggerInterfacePtr logger);
}  // namespace hostApi
}  // namespace python
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
