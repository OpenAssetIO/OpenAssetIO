// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>

#include "../_openassetio.hpp"

void registerManagerFactory(const py::module& mod) {
  using openassetio::hostApi::HostInterfacePtr;
  using openassetio::hostApi::ManagerFactory;
  using openassetio::hostApi::ManagerFactoryPtr;
  using openassetio::hostApi::ManagerImplementationFactoryInterfacePtr;
  using openassetio::hostApi::ManagerPtr;
  using openassetio::log::LoggerInterfacePtr;

  // TODO(DF): `py::final()` once ManagerFactory is fully C++.
  py::class_<ManagerFactory, ManagerFactoryPtr> managerFactory(mod, "ManagerFactory");
  managerFactory
      .def(py::init(RetainCommonPyArgs::forFn<&ManagerFactory::make>()),
           py::arg("hostInterface").none(false),
           py::arg("managerImplementationFactory").none(false), py::arg("logger").none(false))
      .def("identifiers", &ManagerFactory::identifiers);

  py::class_<ManagerFactory::ManagerDetail>(managerFactory, "ManagerDetail")
      .def(py::init<openassetio::Identifier, openassetio::Str, openassetio::InfoDictionary>(),
           py::arg("identifier"), py::arg("displayName"), py::arg("info"))
      .def_readwrite("identifier", &ManagerFactory::ManagerDetail::identifier)
      .def_readwrite("displayName", &ManagerFactory::ManagerDetail::displayName)
      .def_readwrite("info", &ManagerFactory::ManagerDetail::info)
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)

  managerFactory.def("availableManagers", &ManagerFactory::availableManagers)
      .def_readonly_static("kDefaultManagerConfigEnvVarName",
                           &ManagerFactory::kDefaultManagerConfigEnvVarName)
      .def("createManager", &ManagerFactory::createManager, py::arg("identifier"))
      .def_static("createManagerForInterface",
                  RetainCommonPyArgs::forFn<&ManagerFactory::createManagerForInterface>(),
                  py::arg("identifier"), py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false))
      .def_static("defaultManagerForInterface",
                  RetainCommonPyArgs::forFn<static_cast<ManagerPtr (*)(
                      std::string_view, const HostInterfacePtr&,
                      const ManagerImplementationFactoryInterfacePtr&, const LoggerInterfacePtr&)>(
                      &ManagerFactory::defaultManagerForInterface)>(),
                  py::arg("configPath"), py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false))
      .def_static("defaultManagerForInterface",
                  RetainCommonPyArgs::forFn<static_cast<ManagerPtr (*)(
                      const HostInterfacePtr&, const ManagerImplementationFactoryInterfacePtr&,
                      const LoggerInterfacePtr&)>(&ManagerFactory::defaultManagerForInterface)>(),
                  py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false));
}
