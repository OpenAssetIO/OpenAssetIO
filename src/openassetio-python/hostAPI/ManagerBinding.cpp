// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/hostAPI/Manager.hpp>

#include "../_openassetio.hpp"

void registerManager(const py::module& mod) {
  using openassetio::hostAPI::Manager;
  using openassetio::managerAPI::ManagerInterfacePtr;

  // Manager wrapper is cheap and has no independent shared state, so
  // no need for a `shared_ptr` holder.
  py::class_<Manager>(mod, "Manager")
      .def(py::init<ManagerInterfacePtr>(), py::arg("managerInterface").none(false))
      .def("identifier", &Manager::identifier)
      .def("displayName", &Manager::displayName)
      .def("info", &Manager::info);
}
