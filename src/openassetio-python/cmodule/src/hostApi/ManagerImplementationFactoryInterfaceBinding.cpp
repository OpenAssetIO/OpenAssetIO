// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../PyRetainingSharedPtr.hpp"
#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyManagerImplementationFactoryInterface : ManagerImplementationFactoryInterface {
  using ManagerImplementationFactoryInterface::ManagerImplementationFactoryInterface;

  [[nodiscard]] Identifiers identifiers() override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(
        Identifiers, ManagerImplementationFactoryInterface, identifiers,
        /* no args */);
  }

  [[nodiscard]] managerApi::ManagerInterfacePtr instantiate(
      const Identifier& identifier) override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(PyRetainingSharedPtr<managerApi::ManagerInterface>,
                                       ManagerImplementationFactoryInterface, instantiate,
                                       identifier);
  }

  using ManagerImplementationFactoryInterface::logger_;
};

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerManagerImplementationFactoryInterface(const py::module& mod) {
  using openassetio::hostApi::ManagerImplementationFactoryInterface;
  using openassetio::hostApi::ManagerImplementationFactoryInterfacePtr;
  using openassetio::hostApi::PyManagerImplementationFactoryInterface;
  using PyRetainingLoggerInterfacePtr =
      openassetio::PyRetainingSharedPtr<openassetio::log::LoggerInterface>;

  py::class_<ManagerImplementationFactoryInterface, PyManagerImplementationFactoryInterface,
             ManagerImplementationFactoryInterfacePtr>(mod,
                                                       "ManagerImplementationFactoryInterface")
      .def(py::init<PyRetainingLoggerInterfacePtr>(), py::arg("logger").none(false))
      .def("identifiers", &ManagerImplementationFactoryInterface::identifiers,
           py::call_guard<py::gil_scoped_release>{})
      .def("instantiate", &ManagerImplementationFactoryInterface::instantiate,
           py::arg("identifier"), py::call_guard<py::gil_scoped_release>{})
      .def_readonly("_logger", &PyManagerImplementationFactoryInterface::logger_);
}
