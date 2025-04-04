// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

#include <openassetio/pluginSystem/CppPluginSystem.hpp>

// NOLINTBEGIN(misc-include-cleaner) - required for pybind11
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
// NOLINTEND(misc-include-cleaner)

#include "../_openassetio.hpp"

void registerCppPluginSystem(const py::module_ &mod) {
  using openassetio::pluginSystem::CppPluginSystem;

  // Only bother releasing the GIL for `scan`, since that's the only
  // method that potentially calls out to virtual method(s). Tests will
  // catch if this changes (e.g. if we add logger calls in the other
  // methods).

  py::class_<CppPluginSystem, CppPluginSystem::Ptr>(mod, "CppPluginSystem", py::is_final())
      .def(py::init(RetainCommonPyArgs::forFn<&CppPluginSystem::make>()),
           py::arg("logger").none(false))
      .def("reset", &CppPluginSystem::reset)
      .def("scan", &CppPluginSystem::scan, py::arg("paths"), py::arg("pathsEnvVar"),
           py::arg("moduleHookName"), py::arg("validationCallback"),
           py::call_guard<py::gil_scoped_release>{})
      .def("identifiers", &CppPluginSystem::identifiers)
      .def("plugin", &CppPluginSystem::plugin, py::arg("identifier"));
}
