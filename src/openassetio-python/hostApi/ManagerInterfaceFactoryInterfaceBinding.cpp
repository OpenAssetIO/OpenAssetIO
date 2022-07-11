// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/LoggerInterface.hpp>
#include <openassetio/hostApi/ManagerInterfaceFactoryInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyManagerInterfaceFactoryInterface : ManagerInterfaceFactoryInterface {
  using ManagerInterfaceFactoryInterface::ManagerInterfaceFactoryInterface;

  [[nodiscard]] Identifiers identifiers() override {
    PYBIND11_OVERRIDE_PURE(Identifiers, ManagerInterfaceFactoryInterface, identifiers,
                           /* no args */);
  }

  [[nodiscard]] managerApi::ManagerInterfacePtr instantiate(const Str& identifier) override {
    PYBIND11_OVERRIDE_PURE(managerApi::ManagerInterfacePtr, ManagerInterfaceFactoryInterface,
                           instantiate, identifier);
  }

  using ManagerInterfaceFactoryInterface::logger_;
};

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerManagerInterfaceFactoryInterface(const py::module& mod) {
  using openassetio::hostApi::ManagerInterfaceFactoryInterface;
  using openassetio::hostApi::ManagerInterfaceFactoryInterfacePtr;
  using openassetio::hostApi::PyManagerInterfaceFactoryInterface;

  py::class_<ManagerInterfaceFactoryInterface, PyManagerInterfaceFactoryInterface,
             ManagerInterfaceFactoryInterfacePtr>(mod, "ManagerInterfaceFactoryInterface")
      .def(py::init<openassetio::LoggerInterfacePtr>(), py::arg("logger").none(false))
      .def("identifiers", &ManagerInterfaceFactoryInterface::identifiers)
      .def("instantiate", &ManagerInterfaceFactoryInterface::instantiate, py::arg("identifier"))
      .def_readonly("_logger", &PyManagerInterfaceFactoryInterface::logger_);
}
