// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerAPI {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyManagerInterface : ManagerInterface {
  using ManagerInterface::ManagerInterface;

  [[nodiscard]] Str identifier() const override {
    PYBIND11_OVERRIDE_PURE(Str, ManagerInterface, identifier, /* no args */);
  }

  [[nodiscard]] Str displayName() const override {
    PYBIND11_OVERRIDE_PURE(Str, ManagerInterface, displayName, /* no args */);
  }

  [[nodiscard]] InfoDictionary info() const override {
    PYBIND11_OVERRIDE(InfoDictionary, ManagerInterface, info, /* no args */);
  }

  void initialize(HostSessionPtr hostSession) override {
    PYBIND11_OVERRIDE_PURE(void, ManagerInterface, initialize, hostSession);
  }
};

}  // namespace managerAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerManagerInterface(const py::module& mod) {
  using openassetio::managerAPI::ManagerInterface;
  using openassetio::managerAPI::ManagerInterfacePtr;
  using openassetio::managerAPI::PyManagerInterface;

  py::class_<ManagerInterface, PyManagerInterface, ManagerInterfacePtr>(mod, "ManagerInterface")
      .def(py::init())
      .def("identifier", &ManagerInterface::identifier)
      .def("displayName", &ManagerInterface::displayName)
      .def("info", &ManagerInterface::info)
      .def("initialize", &ManagerInterface::initialize);
}
