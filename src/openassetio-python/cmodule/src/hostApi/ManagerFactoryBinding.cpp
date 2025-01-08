// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

void registerManagerFactory(const py::module& mod) {
  using openassetio::hostApi::HostInterfacePtr;
  using openassetio::hostApi::ManagerFactory;
  using openassetio::hostApi::ManagerFactoryPtr;
  using openassetio::hostApi::ManagerImplementationFactoryInterfacePtr;
  using openassetio::hostApi::ManagerPtr;
  using openassetio::log::LoggerInterfacePtr;

  py::class_<ManagerFactory, ManagerFactoryPtr> managerFactory(mod, "ManagerFactory",
                                                               py::is_final());
  managerFactory
      .def(py::init(RetainCommonPyArgs::forFn<&ManagerFactory::make>()),
           py::arg("hostInterface").none(false),
           py::arg("managerImplementationFactory").none(false), py::arg("logger").none(false))
      .def("identifiers", &ManagerFactory::identifiers, py::call_guard<py::gil_scoped_release>{});

  py::class_<ManagerFactory::ManagerDetail>(managerFactory, "ManagerDetail")
      .def(py::init<openassetio::Identifier, openassetio::Str, openassetio::InfoDictionary>(),
           py::arg("identifier"), py::arg("displayName"), py::arg("info"))
      .def_readwrite("identifier", &ManagerFactory::ManagerDetail::identifier)
      .def_readwrite("displayName", &ManagerFactory::ManagerDetail::displayName)
      .def_readwrite("info", &ManagerFactory::ManagerDetail::info)
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)

  managerFactory
      .def("availableManagers", &ManagerFactory::availableManagers,
           py::call_guard<py::gil_scoped_release>{})
      .def_readonly_static("kDefaultManagerConfigEnvVarName",
                           &ManagerFactory::kDefaultManagerConfigEnvVarName)
      .def("createManager", &ManagerFactory::createManager, py::arg("identifier"),
           py::call_guard<py::gil_scoped_release>{})
      .def_static("createManagerForInterface",
                  RetainCommonPyArgs::forFn<&ManagerFactory::createManagerForInterface>(),
                  py::arg("identifier"), py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false), py::call_guard<py::gil_scoped_release>{})
      .def_static("defaultManagerForInterface",
                  RetainCommonPyArgs::forFn<static_cast<ManagerPtr (*)(
                      std::string_view, const HostInterfacePtr&,
                      const ManagerImplementationFactoryInterfacePtr&, const LoggerInterfacePtr&)>(
                      &ManagerFactory::defaultManagerForInterface)>(),
                  py::arg("configPath"), py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false), py::call_guard<py::gil_scoped_release>{})
      .def_static("defaultManagerForInterface",
                  RetainCommonPyArgs::forFn<static_cast<ManagerPtr (*)(
                      const HostInterfacePtr&, const ManagerImplementationFactoryInterfacePtr&,
                      const LoggerInterfacePtr&)>(&ManagerFactory::defaultManagerForInterface)>(),
                  py::arg("hostInterface").none(false),
                  py::arg("managerImplementationFactory").none(false),
                  py::arg("logger").none(false), py::call_guard<py::gil_scoped_release>{});
}
