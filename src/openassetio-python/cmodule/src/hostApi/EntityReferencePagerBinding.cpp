// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/hostApi/EntityReferencePager.hpp>

// NOLINTBEGIN(misc-include-cleaner) - required for pybind11
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
// NOLINTEND(misc-include-cleaner)

#include "../_openassetio.hpp"

void registerEntityReferencePager(const py::module& mod) {
  using openassetio::hostApi::EntityReferencePager;
  using openassetio::hostApi::EntityReferencePagerPtr;

  py::class_<EntityReferencePager, EntityReferencePagerPtr>{mod, "EntityReferencePager",
                                                            py::is_final()}
      .def(py::init(RetainCommonPyArgs::forFn<&EntityReferencePager::make>()),
           py::arg("entityReferencePagerInterface").none(false),
           py::arg("hostSession").none(false))
      .def("hasNext", &EntityReferencePager::hasNext, py::call_guard<py::gil_scoped_release>{})
      .def("get", &EntityReferencePager::get, py::call_guard<py::gil_scoped_release>{})
      .def("next", &EntityReferencePager::next, py::call_guard<py::gil_scoped_release>{});
}
