// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/managerAPI/Host.hpp>
#include <openassetio/managerAPI/HostSession.hpp>

#include "../_openassetio.hpp"

void registerHostSession(const py::module& mod) {
  using openassetio::managerAPI::HostPtr;
  using openassetio::managerAPI::HostSession;
  using openassetio::managerAPI::HostSessionPtr;

  py::class_<HostSession, HostSessionPtr>(mod, "HostSession")
      .def(py::init<HostPtr>(), py::arg("host").none(false))
      .def("host", &HostSession::host);
}
