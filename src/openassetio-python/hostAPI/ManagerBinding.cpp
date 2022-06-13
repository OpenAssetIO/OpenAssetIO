// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/hostAPI/Manager.hpp>

#include "../_openassetio.hpp"

void registerManager(const py::module& mod) {
  using openassetio::hostAPI::Manager;
  using openassetio::hostAPI::ManagerPtr;
  using openassetio::managerAPI::ManagerInterfacePtr;

  py::class_<Manager, ManagerPtr>(mod, "Manager")
      .def(py::init<ManagerInterfacePtr, openassetio::managerAPI::HostSessionPtr>(),
           py::arg("managerInterface").none(false), py::arg("hostSession").none(false))
      .def("identifier", &Manager::identifier)
      .def("displayName", &Manager::displayName)
      .def("info", &Manager::info);
}
