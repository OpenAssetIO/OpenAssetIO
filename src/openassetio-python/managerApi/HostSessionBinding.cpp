// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>

#include "../_openassetio.hpp"

void registerHostSession(const py::module& mod) {
  using openassetio::managerApi::HostPtr;
  using openassetio::managerApi::HostSession;
  using openassetio::managerApi::HostSessionPtr;

  py::class_<HostSession, HostSessionPtr>(mod, "HostSession")
      .def(py::init<HostPtr>(), py::arg("host").none(false))
      .def("host", &HostSession::host);
}
