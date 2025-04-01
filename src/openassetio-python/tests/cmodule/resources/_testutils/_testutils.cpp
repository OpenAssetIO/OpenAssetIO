// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

namespace py = pybind11;

extern void registerPyRetainingSharedPtrTestTypes(py::module_&);
extern void registerExceptionThrower(py::module_& mod);
extern void registerRunInThread(py::module_& mod);
extern void registerCreateHostInterface(py::module_& mod);

extern void registerTestUtils(py::module& mod) {
  py::module_ testutils = mod.def_submodule("_testutils");
  registerPyRetainingSharedPtrTestTypes(testutils);
  registerExceptionThrower(testutils);
  registerRunInThread(testutils);
  registerCreateHostInterface(testutils);
}
