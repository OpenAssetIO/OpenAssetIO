// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
/**
 * Bindings used for testing the C++ Python bridge hostApi helpers.
 */
#include <pybind11/pybind11.h>
#include <openassetio/LoggerInterface.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/python/hostApi.hpp>

namespace py = pybind11;

void registerHostApiTestTypes(py::module_& mod) {
  mod.def("callCreatePythonPluginSystemManagerImplementationFactory",
          [](openassetio::LoggerInterfacePtr logger) {
            openassetio::hostApi::ManagerImplementationFactoryInterfacePtr pluginSystem =
                openassetio::python::hostApi::createPythonPluginSystemManagerImplementationFactory(
                    std::move(logger));
            return pluginSystem;
          });
}
