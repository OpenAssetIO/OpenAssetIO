// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/managerApi/HostSession.hpp>

// NOLINTBEGIN(misc-include-cleaner) - required for pybind11
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
// NOLINTEND(misc-include-cleaner)

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
