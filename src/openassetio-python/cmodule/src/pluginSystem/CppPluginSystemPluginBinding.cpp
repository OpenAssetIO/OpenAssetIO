// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"
#include "../overrideMacros.hpp"

namespace {
using openassetio::pluginSystem::CppPluginSystemPlugin;
struct PyCppPluginSystemPlugin : CppPluginSystemPlugin {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(openassetio::Identifier, CppPluginSystemPlugin, identifier,
                                       /* no args */);
  }
};
}  // namespace

void registerCppPluginSystemPlugin(const py::module_ &mod) {
  using openassetio::pluginSystem::CppPluginSystemPlugin;

  py::class_<CppPluginSystemPlugin, PyCppPluginSystemPlugin, CppPluginSystemPlugin::Ptr>(
      mod, "CppPluginSystemPlugin")
      .def(py::init())
      .def("identifier", &CppPluginSystemPlugin::identifier,
           py::call_guard<py::gil_scoped_release>{});
}
