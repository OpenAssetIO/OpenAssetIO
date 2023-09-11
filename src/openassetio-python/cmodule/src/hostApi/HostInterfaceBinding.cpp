// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyHostInterface : HostInterface {
  using HostInterface::HostInterface;

  [[nodiscard]] Identifier identifier() const override {
    PYBIND11_OVERRIDE_PURE(Identifier, HostInterface, identifier, /* no args */);
  }

  [[nodiscard]] Str displayName() const override {
    PYBIND11_OVERRIDE_PURE(Str, HostInterface, displayName, /* no args */);
  }

  [[nodiscard]] InfoDictionary info() override {
    PYBIND11_OVERRIDE(InfoDictionary, HostInterface, info, /* no args */);
  }
};

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerHostInterface(const py::module& mod) {
  using openassetio::hostApi::HostInterface;
  using openassetio::hostApi::HostInterfacePtr;
  using openassetio::hostApi::PyHostInterface;

  py::class_<HostInterface, PyHostInterface, HostInterfacePtr>(mod, "HostInterface")
      .def(py::init())
      .def("identifier", &HostInterface::identifier)
      .def("displayName", &HostInterface::displayName)
      .def("info", &HostInterface::info);
}
