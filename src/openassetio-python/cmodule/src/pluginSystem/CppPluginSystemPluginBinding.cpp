// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

#include "../_openassetio.hpp"

void registerCppPluginSystemPlugin(const py::module_ &mod) {
  using openassetio::pluginSystem::CppPluginSystemPlugin;

  py::class_<CppPluginSystemPlugin, CppPluginSystemPlugin::Ptr>(mod, "CppPluginSystemPlugin",
                                                                py::is_final())
      .def("identifier", &CppPluginSystemPlugin::identifier,
           py::call_guard<py::gil_scoped_release>{});
}
