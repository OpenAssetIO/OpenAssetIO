// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2024 The Foundry Visionmongers Ltd
#include <sstream>

#include <fmt/format.h>

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/EntityReference.hpp>
#include <openassetio/utils/ostream.hpp>

#include "_openassetio.hpp"

void registerEntityReference(const py::module& mod) {
  using openassetio::EntityReference;

  py::class_<EntityReference>{mod, "EntityReference", py::is_final()}
      .def(py::init<openassetio::Str>(), py::arg("entityReferenceString"))
      .def("toString", &EntityReference::toString)
      .def("__str__",
           [](const EntityReference& self) {
             std::ostringstream stringStream;
             stringStream << self;
             return stringStream.str();
           })
      .def("__repr__",
           [](const EntityReference& self) {
             std::ostringstream stringStream;
             stringStream << self;
             return fmt::format("EntityReference('{}')", stringStream.str());
           })
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)
}
