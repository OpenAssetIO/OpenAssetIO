// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd

#include "_openassetio.hpp"

PYBIND11_MODULE(_openassetio, mod) {
  namespace py = pybind11;

  // Note: the `register` functions here should be called in dependency
  // order. E.g. `Manager` depends on `ManagerInterface`, so
  // `registerManagerInterface` should be called first. This is so
  // pybind11 will properly report type names in its docstring/error
  // output.

  const py::module access = mod.def_submodule("access");
  const py::module managerApi = mod.def_submodule("managerApi");
  const py::module hostApi = mod.def_submodule("hostApi");
  const py::module log = mod.def_submodule("log");
  const py::module constants = mod.def_submodule("constants");
  const py::module errors = mod.def_submodule("errors");

  registerAccess(access);
  registerConstants(constants);
  registerLoggerInterface(log);
  registerConsoleLogger(log);
  registerSeverityFilter(log);
  registerTraitsData(mod);
  registerManagerStateBase(managerApi);
  registerContext(mod);
  registerBatchElementError(errors);
  registerExceptions(errors);
  registerEntityReference(mod);
  registerHostInterface(hostApi);
  registerHost(managerApi);
  registerHostSession(managerApi);
  registerEntityReferencePagerInterface(managerApi);
  registerEntityReferencePager(hostApi);
  registerManagerInterface(managerApi);
  registerManagerImplementationFactoryInterface(hostApi);
  registerManager(hostApi);
  registerManagerFactory(hostApi);
}
