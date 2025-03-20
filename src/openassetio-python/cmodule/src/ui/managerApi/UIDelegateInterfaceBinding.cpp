// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

#include "../../_openassetio.hpp"
#include "../../overrideMacros.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

// TODO(DF): fill out details

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyUIDelegateInterface : UIDelegateInterface {
  using UIDelegateInterface::UIDelegateInterface;

  [[nodiscard]] Identifier identifier() const override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(Identifier, UIDelegateInterface, identifier, /* no args */);
  }

  [[nodiscard]] InfoDictionary info() override {
    OPENASSETIO_PYBIND11_OVERRIDE(InfoDictionary, UIDelegateInterface, info, /* no args */);
  }
};

}  // namespace ui::managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerUIDelegateInterface(const py::module& mod) {
  using openassetio::ui::managerApi::PyUIDelegateInterface;
  using openassetio::ui::managerApi::UIDelegateInterface;
  using openassetio::ui::managerApi::UIDelegateInterfacePtr;

  py::class_<UIDelegateInterface, PyUIDelegateInterface, UIDelegateInterfacePtr>(
      mod, "UIDelegateInterface")
      .def(py::init())
      .def("identifier", &UIDelegateInterface::identifier,
           py::call_guard<py::gil_scoped_release>{})
      .def("info", &UIDelegateInterface::info, py::call_guard<py::gil_scoped_release>{});
}
