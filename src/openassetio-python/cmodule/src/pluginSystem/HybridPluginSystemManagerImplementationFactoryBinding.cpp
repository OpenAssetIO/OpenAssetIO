// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <algorithm>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/pluginSystem/HybridPluginSystemManagerImplementationFactory.hpp>

#include "../_openassetio.hpp"
#include "../overrideMacros.hpp"

void registerHybridPluginSystemManagerImplementationFactory(const py::module_& mod) {
  using openassetio::hostApi::ManagerImplementationFactoryInterface;
  using openassetio::log::LoggerInterface;
  using openassetio::managerApi::ManagerInterface;
  using openassetio::pluginSystem::HybridPluginSystemManagerImplementationFactory;

  // We must ensure any Python facade implementing a "subclass" is not
  // destroyed whilst the C++ instance is alive. The
  // PyRetainingSharedPtr mechanism ensures the Python object lifetime
  // is linked to the shared_ptr lifetime.
  using openassetio::PyRetainingSharedPtr;
  using PyRetainingLoggerInterfacePtr = PyRetainingSharedPtr<LoggerInterface>;
  using PyRetainingManagerImplFactoryPtrs =
      std::vector<PyRetainingSharedPtr<ManagerImplementationFactoryInterface>>;

  py::class_<HybridPluginSystemManagerImplementationFactory, ManagerImplementationFactoryInterface,
             HybridPluginSystemManagerImplementationFactory::Ptr>(
      mod, "HybridPluginSystemManagerImplementationFactory", py::is_final())
      .def(py::init([](PyRetainingManagerImplFactoryPtrs factories,
                       PyRetainingLoggerInterfacePtr logger) {
             if (any_of(cbegin(factories), cend(factories),
                        std::logical_not<PyRetainingManagerImplFactoryPtrs::value_type>{})) {
               throw openassetio::errors::InputValidationException{
                   "HybridPluginSystem: Manager implementation factory cannot be None"};
             }

             return HybridPluginSystemManagerImplementationFactory::make(
                 {make_move_iterator(begin(factories)), make_move_iterator(end(factories))},
                 std::move(logger));
           }),
           py::arg("factories"), py::arg("logger").none(false))
      .def("identifiers", &HybridPluginSystemManagerImplementationFactory::identifiers,
           py::call_guard<py::gil_scoped_release>{})
      .def("instantiate", &HybridPluginSystemManagerImplementationFactory::instantiate,
           py::arg("identifier"), py::call_guard<py::gil_scoped_release>{});
}
