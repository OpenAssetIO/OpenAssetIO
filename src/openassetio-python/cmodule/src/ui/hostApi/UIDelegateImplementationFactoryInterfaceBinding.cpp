// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <pybind11/stl.h>

#include <openassetio/export.h>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

#include "../../PyRetainingSharedPtr.hpp"
#include "../../_openassetio.hpp"
#include "../../overrideMacros.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyUIDelegateImplementationFactoryInterface : UIDelegateImplementationFactoryInterface {
  using UIDelegateImplementationFactoryInterface::UIDelegateImplementationFactoryInterface;

  [[nodiscard]] Identifiers identifiers() override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(
        Identifiers, UIDelegateImplementationFactoryInterface, identifiers,
        /* no args */);
  }

  [[nodiscard]] managerApi::UIDelegateInterfacePtr instantiate(
      const Identifier& identifier) override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(PyRetainingSharedPtr<managerApi::UIDelegateInterface>,
                                       UIDelegateImplementationFactoryInterface, instantiate,
                                       identifier);
  }

  using UIDelegateImplementationFactoryInterface::logger;
};

}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerUIDelegateImplementationFactoryInterface(const py::module& mod) {
  using openassetio::ui::hostApi::PyUIDelegateImplementationFactoryInterface;
  using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterface;
  using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterfacePtr;
  using PyRetainingLoggerInterfacePtr =
      openassetio::PyRetainingSharedPtr<openassetio::log::LoggerInterface>;

  py::class_<UIDelegateImplementationFactoryInterface, PyUIDelegateImplementationFactoryInterface,
             UIDelegateImplementationFactoryInterfacePtr>(
      mod, "UIDelegateImplementationFactoryInterface")
      .def(py::init<PyRetainingLoggerInterfacePtr>(), py::arg("logger").none(false))
      .def("identifiers", &UIDelegateImplementationFactoryInterface::identifiers,
           py::call_guard<py::gil_scoped_release>{})
      .def("instantiate", &UIDelegateImplementationFactoryInterface::instantiate,
           py::arg("identifier"), py::call_guard<py::gil_scoped_release>{})
      .def_property_readonly("_logger", &PyUIDelegateImplementationFactoryInterface::logger);
}
