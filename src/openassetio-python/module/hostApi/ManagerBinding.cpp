// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>

#include "../_openassetio.hpp"

void registerManager(const py::module& mod) {
  using openassetio::hostApi::Manager;
  using openassetio::hostApi::ManagerPtr;
  using openassetio::managerApi::ManagerInterfacePtr;

  py::class_<Manager, ManagerPtr>(mod, "Manager")
      .def(py::init(RetainCommonPyArgs::forFn<&Manager::make>()),
           py::arg("managerInterface").none(false), py::arg("hostSession").none(false))
      .def("identifier", &Manager::identifier)
      .def("displayName", &Manager::displayName)
      .def("info", &Manager::info)
      .def("settings", &Manager::settings)
      .def("initialize", &Manager::initialize, py::arg("managerSettings"))
      .def("managementPolicy", &Manager::managementPolicy, py::arg("traitSet"),
           py::arg("context").none(false))
      .def("createContext", &Manager::createContext)
      .def("createChildContext", &Manager::createChildContext,
           py::arg("parentContext").none(false))
      .def("persistenceTokenForContext", &Manager::persistenceTokenForContext,
           py::arg("context").none(false))
      .def("contextFromPersistenceToken", &Manager::contextFromPersistenceToken, py::arg("token"))
      .def("isEntityReferenceString", &Manager::isEntityReferenceString, py::arg("someString"))
      .def("createEntityReference", &Manager::createEntityReference,
           py::arg("entityReferenceString"))
      .def("createEntityReferenceIfValid", &Manager::createEntityReferenceIfValid,
           py::arg("entityReferenceString"))
      .def("resolve", &Manager::resolve, py::arg("entityReferences"), py::arg("traitSet"),
           py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"));
}
