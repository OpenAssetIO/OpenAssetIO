// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

namespace py = pybind11;

void registerPyRetainingSharedPtrTestTypes(const py::module_&);

PYBIND11_MODULE(_openassetio_test, mod) { registerPyRetainingSharedPtrTestTypes(mod); }
