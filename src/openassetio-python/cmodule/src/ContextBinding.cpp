// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>

#include "PyRetainingSharedPtr.hpp"
#include "_openassetio.hpp"

void registerContext(const py::module& mod) {
  using openassetio::Context;
  using openassetio::ContextPtr;
  using openassetio::TraitsDataPtr;
  using openassetio::managerApi::ManagerStateBasePtr;
  using PyRetainingManagerStateBasePtr =
      openassetio::PyRetainingSharedPtr<openassetio::managerApi::ManagerStateBase>;

  py::class_<Context, ContextPtr> context{mod, "Context", py::is_final()};

  py::enum_<Context::Access>{context, "Access"}
      .value("kRead", Context::Access::kRead)
      .value("kWrite", Context::Access::kWrite)
      .value("kCreateRelated", Context::Access::kCreateRelated)
      .value("kUnknown", Context::Access::kUnknown);

  context.def_readonly_static("kAccessNames", &Context::kAccessNames);

  context
      .def(py::init(RetainCommonPyArgs::forFn<&Context::make>()),
           py::arg_v("access", Context::Access::kUnknown), py::arg_v("locale", TraitsDataPtr{}),
           py::arg_v("managerState", ManagerStateBasePtr{}))
      .def_readwrite("access", &Context::access)
      .def_readwrite("locale", &Context::locale)
      .def_property(
          "managerState", [](const Context& self) { return self.managerState; },
          [](Context& self, PyRetainingManagerStateBasePtr managerState) {
            self.managerState = std::move(managerState);
          })
      .def("isForRead", &Context::isForRead)
      .def("isForWrite", &Context::isForWrite);
}
