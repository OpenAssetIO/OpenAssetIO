// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include "_openassetio.hpp"

PYBIND11_MODULE(_openassetio, mod) {
  namespace py = pybind11;

  // Note: the `register` functions here should be called in dependency
  // order. E.g. `Manager` depends on `ManagerInterface`, so
  // `registerManagerInterface` should be called first. This is so
  // pybind11 will properly report type names in its docstring/error
  // output.

  py::module managerAPI = mod.def_submodule("managerAPI");

  registerManagerInterface(managerAPI);

  py::module hostAPI = mod.def_submodule("hostAPI");

  registerManager(hostAPI);

  py::module specification = mod.def_submodule("specification");

  registerSpecification(specification);
}
