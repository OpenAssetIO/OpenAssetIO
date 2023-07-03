// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <algorithm>

#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/BatchElementError.hpp>
#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/trait/collection.hpp>

#include "../_openassetio.hpp"

void registerEntityReferencePager(const py::module& mod) {
  using openassetio::hostApi::EntityReferencePager;
  using openassetio::hostApi::EntityReferencePagerPtr;

  py::class_<EntityReferencePager, EntityReferencePagerPtr>{mod, "EntityReferencePager"}
      .def(py::init(RetainCommonPyArgs::forFn<&EntityReferencePager::make>()),
           py::arg("entityReferencePagerInterface").none(false),
           py::arg("hostSession").none(false))
      .def("hasNext", &EntityReferencePager::hasNext)
      .def("get", &EntityReferencePager::get)
      .def("next", &EntityReferencePager::next);
}
