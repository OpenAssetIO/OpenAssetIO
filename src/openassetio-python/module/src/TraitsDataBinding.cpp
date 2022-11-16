// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <optional>

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <openassetio/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>

#include "_openassetio.hpp"

void registerTraitsData(const py::module& mod) {
  using openassetio::TraitsData;
  using openassetio::TraitsDataConstPtr;
  using openassetio::TraitsDataPtr;
  namespace trait = openassetio::trait;
  namespace property = openassetio::trait::property;
  using MaybeValue = std::optional<property::Value>;

  py::class_<TraitsData, TraitsDataPtr>(mod, "TraitsData", py::is_final())
      .def(py::init(static_cast<TraitsDataPtr (*)()>(&TraitsData::make)))
      .def(py::init(static_cast<TraitsDataPtr (*)(const trait::TraitSet&)>(&TraitsData::make)),
           py::arg("traitSet"))
      .def(py::init(static_cast<TraitsDataPtr (*)(const TraitsDataConstPtr&)>(&TraitsData::make)),
           py::arg("other"))
      .def("traitSet", &TraitsData::traitSet)
      .def("hasTrait", &TraitsData::hasTrait, py::arg("traitId"))
      .def("addTrait", &TraitsData::addTrait, py::arg("traitId"))
      .def("addTraits", &TraitsData::addTraits, py::arg("traitSet"))
      .def("setTraitProperty", &TraitsData::setTraitProperty, py::arg("traitId"),
           py::arg("propertyKey"), py::arg("propertyValue").none(false))
      .def(
          "getTraitProperty",
          [](const TraitsData& self, const trait::TraitId& traitId,
             const property::Key& propertyKey) -> MaybeValue {
            if (property::Value out; self.getTraitProperty(&out, traitId, propertyKey)) {
              return out;
            }
            return {};
          },
          py::arg("traitId"), py::arg("propertyKey"))
      .def("traitPropertyKeys", &TraitsData::traitPropertyKeys, py::arg("traitId"))
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)
}
