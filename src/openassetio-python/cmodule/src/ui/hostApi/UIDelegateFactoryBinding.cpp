// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegate.hpp>
#include <openassetio/ui/hostApi/UIDelegateFactory.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>

#include "../../_openassetio.hpp"

void registerUIDelegateFactory(const py::module& mod) {
  using openassetio::hostApi::HostInterfacePtr;
  using openassetio::log::LoggerInterfacePtr;
  using openassetio::ui::hostApi::UIDelegateFactory;
  using openassetio::ui::hostApi::UIDelegateFactoryPtr;
  using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterfacePtr;
  using openassetio::ui::hostApi::UIDelegatePtr;

  py::class_<UIDelegateFactory, UIDelegateFactoryPtr> uiDelegateFactory(mod, "UIDelegateFactory",
                                                                        py::is_final());
  uiDelegateFactory
      .def(py::init(RetainCommonPyArgs::forFn<&UIDelegateFactory::make>()),
           py::arg("hostInterface").none(false),
           py::arg("managerImplementationFactory").none(false), py::arg("logger").none(false))
      .def("identifiers", &UIDelegateFactory::identifiers,
           py::call_guard<py::gil_scoped_release>{});

  py::class_<UIDelegateFactory::UIDelegateDetail>(uiDelegateFactory, "UIDelegateDetail")
      .def(py::init<openassetio::Identifier, openassetio::Str, openassetio::InfoDictionary>(),
           py::arg("identifier"), py::arg("displayName"), py::arg("info"))
      .def_readwrite("identifier", &UIDelegateFactory::UIDelegateDetail::identifier)
      .def_readwrite("displayName", &UIDelegateFactory::UIDelegateDetail::displayName)
      .def_readwrite("info", &UIDelegateFactory::UIDelegateDetail::info)
      // ReSharper disable once CppIdenticalOperandsInBinaryExpression
      .def(py::self == py::self);  // NOLINT(misc-redundant-expression)

  uiDelegateFactory
      .def("availableUIDelegates", &UIDelegateFactory::availableUIDelegates,
           py::call_guard<py::gil_scoped_release>{})
      .def_readonly_static("kDefaultUIDelegateConfigEnvVarName",
                           &UIDelegateFactory::kDefaultUIDelegateConfigEnvVarName)
      .def("createUIDelegate", &UIDelegateFactory::createUIDelegate, py::arg("identifier"),
           py::call_guard<py::gil_scoped_release>{})
      .def_static("createUIDelegateForInterface",
                  RetainCommonPyArgs::forFn<&UIDelegateFactory::createUIDelegateForInterface>(),
                  py::arg("identifier"), py::arg("hostInterface").none(false),
                  py::arg("uiDelegateImplementationFactory").none(false),
                  py::arg("logger").none(false), py::call_guard<py::gil_scoped_release>{})
      .def_static(
          "defaultUIDelegateForInterface",
          RetainCommonPyArgs::forFn<static_cast<UIDelegatePtr (*)(
              std::string_view, const HostInterfacePtr&,
              const UIDelegateImplementationFactoryInterfacePtr&, const LoggerInterfacePtr&)>(
              &UIDelegateFactory::defaultUIDelegateForInterface)>(),
          py::arg("configPath"), py::arg("hostInterface").none(false),
          py::arg("uiDelegateImplementationFactory").none(false), py::arg("logger").none(false),
          py::call_guard<py::gil_scoped_release>{})
      .def_static(
          "defaultUIDelegateForInterface",
          RetainCommonPyArgs::forFn<static_cast<UIDelegatePtr (*)(
              const HostInterfacePtr&, const UIDelegateImplementationFactoryInterfacePtr&,
              const LoggerInterfacePtr&)>(&UIDelegateFactory::defaultUIDelegateForInterface)>(),
          py::arg("hostInterface").none(false),
          py::arg("uiDelegateImplementationFactory").none(false), py::arg("logger").none(false),
          py::call_guard<py::gil_scoped_release>{});
}
