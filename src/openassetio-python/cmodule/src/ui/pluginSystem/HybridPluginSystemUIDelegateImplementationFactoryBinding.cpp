// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <algorithm>
#include <functional>
#include <iterator>
#include <utility>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>
#include <openassetio/ui/pluginSystem/HybridPluginSystemUIDelegateImplementationFactory.hpp>

#include "../../PyRetainingSharedPtr.hpp"
#include "../../_openassetio.hpp"

void registerHybridPluginSystemUIDelegateImplementationFactory(const py::module_& mod) {
  using openassetio::log::LoggerInterface;
  using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterface;
  using openassetio::ui::managerApi::UIDelegateInterface;
  using openassetio::ui::pluginSystem::HybridPluginSystemUIDelegateImplementationFactory;

  // We must ensure any Python facade implementing a "subclass" is not
  // destroyed whilst the C++ instance is alive. The
  // PyRetainingSharedPtr mechanism ensures the Python object lifetime
  // is linked to the shared_ptr lifetime.
  using openassetio::PyRetainingSharedPtr;
  using PyRetainingLoggerInterfacePtr = PyRetainingSharedPtr<LoggerInterface>;
  using PyRetainingUIDelegateImplFactoryPtrs =
      std::vector<PyRetainingSharedPtr<UIDelegateImplementationFactoryInterface>>;

  py::class_<HybridPluginSystemUIDelegateImplementationFactory,
             UIDelegateImplementationFactoryInterface,
             HybridPluginSystemUIDelegateImplementationFactory::Ptr>(
      mod, "HybridPluginSystemUIDelegateImplementationFactory", py::is_final())
      .def(py::init([](PyRetainingUIDelegateImplFactoryPtrs factories,
                       PyRetainingLoggerInterfacePtr logger) {
             if (any_of(cbegin(factories), cend(factories),
                        std::logical_not<PyRetainingUIDelegateImplFactoryPtrs::value_type>{})) {
               throw openassetio::errors::InputValidationException{
                   "HybridPluginSystem: UI delegate implementation factory cannot be None"};
             }

             return HybridPluginSystemUIDelegateImplementationFactory::make(
                 {make_move_iterator(begin(factories)), make_move_iterator(end(factories))},
                 std::move(logger));
           }),
           py::arg("factories"), py::arg("logger").none(false))
      .def("identifiers", &HybridPluginSystemUIDelegateImplementationFactory::identifiers,
           py::call_guard<py::gil_scoped_release>{})
      .def("instantiate", &HybridPluginSystemUIDelegateImplementationFactory::instantiate,
           py::arg("identifier"), py::call_guard<py::gil_scoped_release>{});
}
