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

  py::module managerApi = mod.def_submodule("managerApi");
  py::module hostApi = mod.def_submodule("hostApi");

  registerLoggerInterface(mod);
  registerTraitsData(mod);
  registerManagerStateBase(managerApi);
  registerContext(mod);
  registerHostInterface(hostApi);
  registerHost(managerApi);
  registerHostSession(managerApi);
  registerManagerInterface(managerApi);
  registerManagerImplementationFactoryInterface(hostApi);
  registerManager(hostApi);
  registerManagerFactory(hostApi);
}
