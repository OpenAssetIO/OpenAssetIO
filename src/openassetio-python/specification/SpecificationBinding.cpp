// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <optional>

#include <pybind11/stl.h>

#include <openassetio/specification/Specification.hpp>

#include "../_openassetio.hpp"

void registerSpecification(const py::module& mod) {
  using openassetio::specification::Specification;
  namespace trait = openassetio::trait;
  namespace property = openassetio::trait::property;
  using MaybeValue = std::optional<property::Value>;

  py::class_<Specification, Holder<Specification>>(mod, "Specification")
      .def(py::init<const Specification::TraitIds&>(), py::arg("traitIds"))
      .def("hasTrait", &Specification::hasTrait, py::arg("id"))
      .def("setTraitProperty", &Specification::setTraitProperty, py::arg("id"),
           py::arg("propertyKey"), py::arg("propertyValue").none(false))
      .def(
          "getTraitProperty",
          [](const Specification& self, const trait::TraitId& traitId,
             const property::Key& key) -> MaybeValue {
            if (property::Value out; self.getTraitProperty(&out, traitId, key)) {
              return out;
            }
            return {};
          },
          py::arg("id"), py::arg("key"));
}
