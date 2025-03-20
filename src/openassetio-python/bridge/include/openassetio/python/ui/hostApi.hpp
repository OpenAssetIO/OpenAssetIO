// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once
#include <openassetio/export.h>
#include <openassetio/python/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(ui::hostApi, UIDelegateImplementationFactoryInterface)
OPENASSETIO_FWD_DECLARE(log, LoggerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::ui::hostApi {
/**
 * Retrieve an instance of the Python UI delegate plugin system
 * implementation.
 *
 * @return Python plugin system.
 */
OPENASSETIO_PYTHON_BRIDGE_EXPORT
openassetio::ui::hostApi::UIDelegateImplementationFactoryInterfacePtr
createPythonPluginSystemUIDelegateImplementationFactory(log::LoggerInterfacePtr logger);
}  // namespace python::ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
