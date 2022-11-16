// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/log/SeverityFilter.hpp>

#include "../PyRetainingSharedPtr.hpp"
#include "../_openassetio.hpp"

void registerSeverityFilter(const py::module& mod) {
  using openassetio::log::LoggerInterface;
  using openassetio::log::SeverityFilter;
  using openassetio::log::SeverityFilterPtr;

  py::class_<SeverityFilter, LoggerInterface, SeverityFilterPtr>(mod, "SeverityFilter",
                                                                 py::is_final())
      .def(py::init(RetainCommonPyArgs::forFn<&SeverityFilter::make>()),
           py::arg("upstreamLogger").none(false))
      .def("getSeverity", &SeverityFilter::getSeverity)
      .def("setSeverity", &SeverityFilter::setSeverity)
      .def("upstreamLogger", &SeverityFilter::upstreamLogger);
}
