// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <optional>

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <openassetio/TraitsData.hpp>

#include "_openassetio.hpp"

void registerTraitsData(const py::module& mod) {
  using openassetio::TraitsData;
  namespace trait = openassetio::trait;
  namespace property = openassetio::trait::property;
  using MaybeValue = std::optional<property::Value>;

  py::class_<TraitsData, Holder<TraitsData>>(mod, "TraitsData", py::is_final())
      .def(py::init())
      .def(py::init<const TraitsData::TraitIds&>(), py::arg("traitIds"))
      .def(py::init<const TraitsData&>())
      .def("traitIds", &TraitsData::traitIds)
      .def("hasTrait", &TraitsData::hasTrait, py::arg("id"))
      .def("addTrait", &TraitsData::addTrait)
      .def("addTraits", &TraitsData::addTraits)
      .def("setTraitProperty", &TraitsData::setTraitProperty, py::arg("id"),
           py::arg("propertyKey"), py::arg("propertyValue").none(false))
      .def(
          "getTraitProperty",
          [](const TraitsData& self, const trait::TraitId& traitId,
             const property::Key& key) -> MaybeValue {
            if (property::Value out; self.getTraitProperty(&out, traitId, key)) {
              return out;
            }
            return {};
          },
          py::arg("id"), py::arg("key"))
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)
}
