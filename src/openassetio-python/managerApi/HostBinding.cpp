// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/managerApi/Host.hpp>

#include "../_openassetio.hpp"

void registerHost(const py::module& mod) {
  using openassetio::hostApi::HostInterfacePtr;
  using openassetio::managerApi::Host;
  using openassetio::managerApi::HostPtr;

  py::class_<Host, HostPtr>(mod, "Host", py::is_final())
      .def(py::init(&Host::make), py::arg("hostInterface").none(false))
      .def("identifier", &Host::identifier)
      .def("displayName", &Host::displayName)
      .def("info", &Host::info);
}
