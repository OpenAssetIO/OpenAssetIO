// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/EntityReference.hpp>

#include "_openassetio.hpp"

void registerEntityReference(const py::module &mod) {
  using openassetio::EntityReference;

  py::class_<EntityReference>{mod, "EntityReference", py::is_final()}
      .def(py::init<openassetio::Str>(), py::arg("entityReferenceString"))
      .def("toString", &EntityReference::toString)
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)
}
