// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>

#include "../_openassetio.hpp"

void registerCppPluginSystem(const py::module_ &mod) {
  using openassetio::pluginSystem::CppPluginSystem;

  py::class_<CppPluginSystem, CppPluginSystem::Ptr>(mod, "CppPluginSystem")
      .def(py::init(RetainCommonPyArgs::forFn<&CppPluginSystem::make>()),
           py::arg("logger").none(false))
      .def("scan", &CppPluginSystem::scan, py::arg("paths"))
      .def("identifiers", &CppPluginSystem::identifiers);
}
