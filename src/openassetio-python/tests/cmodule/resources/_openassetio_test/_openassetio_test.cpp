// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

namespace py = pybind11;

void registerPyRetainingSharedPtrTestTypes(py::module_&);
void registerExceptionThrower(py::module_& mod);
void registerRunInThread(py::module_& mod);

PYBIND11_MODULE(_openassetio_test, mod) {
  registerPyRetainingSharedPtrTestTypes(mod);
  registerExceptionThrower(mod);
  registerRunInThread(mod);
}
