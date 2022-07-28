// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>

#include "../PyRetainingSharedPtr.hpp"
#include "../_openassetio.hpp"

void registerHostSession(const py::module& mod) {
  using openassetio::managerApi::HostSession;
  using openassetio::managerApi::HostSessionPtr;

  py::class_<HostSession, HostSessionPtr>(mod, "HostSession", py::is_final())
      .def(py::init(RetainCommonPyArgs::forFn<&HostSession::make>()), py::arg("host").none(false),
           py::arg("logger").none(false))
      .def("host", &HostSession::host)
      .def("logger", &HostSession::logger);
}
