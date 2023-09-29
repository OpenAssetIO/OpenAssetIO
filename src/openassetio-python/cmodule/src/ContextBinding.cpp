// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitsData.hpp>

#include "PyRetainingSharedPtr.hpp"
#include "_openassetio.hpp"

void registerContext(const py::module& mod) {
  using openassetio::Context;
  using openassetio::ContextPtr;
  using openassetio::managerApi::ManagerStateBasePtr;
  using openassetio::trait::TraitsDataPtr;
  using PyRetainingManagerStateBasePtr =
      openassetio::PyRetainingSharedPtr<openassetio::managerApi::ManagerStateBase>;

  py::class_<Context, ContextPtr> context{mod, "Context", py::is_final()};

  context
      .def(py::init(RetainCommonPyArgs::forFn<&Context::make>()),
           py::arg_v("locale", TraitsDataPtr{}), py::arg_v("managerState", ManagerStateBasePtr{}))
      .def_readwrite("locale", &Context::locale)
      .def_property(
          "managerState", [](const Context& self) { return self.managerState; },
          [](Context& self, PyRetainingManagerStateBasePtr managerState) {
            self.managerState = std::move(managerState);
          });
}
