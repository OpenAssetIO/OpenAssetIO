// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
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
};

}  // namespace managerAPI
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio

void registerManagerInterface(const py::module& mod) {
  using openassetio::managerAPI::ManagerInterface;
  using openassetio::managerAPI::PyManagerInterface;

  py::class_<ManagerInterface, PyManagerInterface, Holder<ManagerInterface>>(mod,
                                                                             "ManagerInterface")
      .def(py::init())
      .def("identifier", &ManagerInterface::identifier)
      .def("displayName", &ManagerInterface::displayName);
}
