// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <sstream>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/utils/ostream.hpp>

#include "PyRetainingSharedPtr.hpp"
#include "_openassetio.hpp"

void registerContext(const py::module& mod) {
  using openassetio::Context;
  using openassetio::ContextPtr;
  using openassetio::managerApi::ManagerStateBasePtr;
  using openassetio::trait::TraitsData;
  using PyRetainingTraitsDataPtr = openassetio::PyRetainingSharedPtr<TraitsData>;
  using PyRetainingManagerStateBasePtr =
      openassetio::PyRetainingSharedPtr<openassetio::managerApi::ManagerStateBase>;

  py::class_<Context, ContextPtr> context{mod, "Context", py::is_final()};

  context
      .def(py::init(
               [](PyRetainingTraitsDataPtr locale, PyRetainingManagerStateBasePtr managerState) {
                 return Context::make(std::move(locale), std::move(managerState));
               }),
           py::arg("locale").none(false), py::arg("managerState") = ManagerStateBasePtr{})
      // Allow no-argument construction. Must use a separate constructor
      // overload, rather than use a default value for `locale` above,
      // since we must create a new `TraitsData` rather than re-use the
      // same default `TraitsData` instance, where any mutations will
      // persist in the default.
      .def(py::init([] { return Context::make(TraitsData::make(), ManagerStateBasePtr{}); }))
      .def("__str__",
           [](const Context& self) {
             std::ostringstream stringStream;
             stringStream << self;
             return stringStream.str();
           })
      .def_readwrite("locale", &Context::locale)
      .def_property(
          "managerState", [](const Context& self) { return self.managerState; },
          [](Context& self, PyRetainingManagerStateBasePtr managerState) {
            self.managerState = std::move(managerState);
          });
}
