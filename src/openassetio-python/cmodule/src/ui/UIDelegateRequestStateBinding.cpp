// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
/**
 * Python bindings for the UIDelegateRequest/State[Interface] classes.
 *
 * We must define these all together due to the circular references
 * caused by the callback functions. I.e. we need to "forward declare"
 * bindings so that pybind11 can properly construct docstrings.
 */

#include <any>
#include <optional>
#include <string>

#include <fmt/core.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/export.h>
#include <openassetio/EntityReference.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateState.hpp>
#include <openassetio/ui/managerApi/UIDelegateRequest.hpp>
#include <openassetio/ui/managerApi/UIDelegateStateInterface.hpp>

#include "../_openassetio.hpp"
#include "../overrideMacros.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui {
namespace hostApi {

/**
 * pybind11 trampoline class to call Python subclass implementation.
 *
 * Ensure the nativeData() implementation always stores a PyObject*.
 *
 * Note the py::handle -> std::any in pyNativeData(), followed by the
 * std::any -> py::handle -> PyObject* -> std::any in nativeData(). This
 * dance is required to work around the implementation of the PYBIND11
 * macros.
 */
struct PyUIDelegateRequestInterface : UIDelegateRequestInterface {
  [[nodiscard]] std::any nativeData() override {
    return std::any_cast<py::handle>(pyNativeData()).ptr();
  }

  [[nodiscard]] std::any pyNativeData() {
    OPENASSETIO_PYBIND11_OVERRIDE(py::handle, UIDelegateRequestInterface, nativeData,
                                  /* no args */);
  }

  [[nodiscard]] EntityReferences entityReferences() override {
    OPENASSETIO_PYBIND11_OVERRIDE(EntityReferences, UIDelegateRequestInterface, entityReferences,
                                  /* no args */);
  }

  [[nodiscard]] trait::TraitsDatas entityTraitsDatas() override {
    OPENASSETIO_PYBIND11_OVERRIDE(
        trait::TraitsDatas, UIDelegateRequestInterface, entityTraitsDatas, /* no args */);
  }

  [[nodiscard]] std::optional<StateChangedCallback> stateChangedCallback() override {
    OPENASSETIO_PYBIND11_OVERRIDE(
        std::optional<StateChangedCallback>, UIDelegateRequestInterface, stateChangedCallback,
        /* no args */);
  }
};
}  // namespace hostApi
namespace managerApi {
/**
 * pybind11 trampoline class to call Python subclass implementation.
 *
 * Ensure the nativeData() implementation always stores a PyObject*.
 *
 * Note the py::handle -> std::any in pyNativeData(), followed by the
 * std::any -> py::handle -> PyObject* -> std::any in nativeData(). This
 * dance is required to work around the implementation of the PYBIND11
 * macros.
 */
struct PyUIDelegateStateInterface : UIDelegateStateInterface {
  [[nodiscard]] std::any nativeData() override {
    return std::any_cast<py::handle>(pyNativeData()).ptr();
  }
  [[nodiscard]] std::any pyNativeData() {
    OPENASSETIO_PYBIND11_OVERRIDE(py::handle, UIDelegateStateInterface, nativeData,
                                  /* no args */);
  }
  [[nodiscard]] EntityReferences entityReferences() override {
    OPENASSETIO_PYBIND11_OVERRIDE(EntityReferences, UIDelegateStateInterface, entityReferences,
                                  /* no args */);
  }

  [[nodiscard]] trait::TraitsDatas entityTraitsDatas() override {
    OPENASSETIO_PYBIND11_OVERRIDE(trait::TraitsDatas, UIDelegateStateInterface, entityTraitsDatas,
                                  /* no args */);
  }

  [[nodiscard]] std::optional<UpdateRequestCallback> updateRequestCallback() override {
    OPENASSETIO_PYBIND11_OVERRIDE(
        std::optional<UpdateRequestCallback>, UIDelegateStateInterface, updateRequestCallback,
        /* no args */);
  }
};
}  // namespace managerApi
}  // namespace ui
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

namespace {

/**
 * Extract a PyObject* from a std::any, and throw an error if the
 * std::any does not contain a PyObject*.
 */
py::object anyCastToPyObject(const std::any& wrapped) {
  if (!wrapped.has_value()) {
    return py::none{};
  }

  // Hosts, managers and middleware should bundle a CPython PyObject* in
  // their std::any.
  if (wrapped.type() == typeid(PyObject*)) {
    return py::reinterpret_borrow<py::object>(std::any_cast<PyObject*>(wrapped));
  }

  // Use pybind11 utility to demangle the typeid.
  std::string wrappedTypeName = wrapped.type().name();
  py::detail::clean_type_id(wrappedTypeName);

  throw openassetio::errors::InputValidationException{
      fmt::format("Python UI delegates only accept Python objects: C++ type '{}' is not supported",
                  wrappedTypeName)};
}
}  // namespace

// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
void registerUIDelegateRequestState(const py::module& hostApi, const py::module& managerApi) {
  using openassetio::EntityReferences;
  using openassetio::trait::TraitsDataPtr;
  using openassetio::trait::TraitsDatas;
  using openassetio::ui::hostApi::PyUIDelegateRequestInterface;
  using openassetio::ui::hostApi::UIDelegateRequestInterface;
  using openassetio::ui::hostApi::UIDelegateState;
  using openassetio::ui::managerApi::PyUIDelegateStateInterface;
  using openassetio::ui::managerApi::UIDelegateRequest;
  using openassetio::ui::managerApi::UIDelegateStateInterface;

  // Note: we "forward declare" the classes, since they have a circular
  // dependency, and pybind11 needs the types available to calculate
  // docstrings.
  py::class_<UIDelegateRequestInterface, PyUIDelegateRequestInterface,
             UIDelegateRequestInterface::Ptr>
      pyUIDelegateRequestInterface(hostApi, "UIDelegateRequestInterface");

  py::class_<UIDelegateStateInterface, PyUIDelegateStateInterface, UIDelegateStateInterface::Ptr>
      pyUIDelegateStateInterface(managerApi, "UIDelegateStateInterface");

  py::class_<UIDelegateRequest, UIDelegateRequest::Ptr> pyUIDelegateRequest(managerApi,
                                                                            "UIDelegateRequest");

  py::class_<UIDelegateState, UIDelegateState::Ptr> pyUIDelegateState(hostApi, "UIDelegateState");

  pyUIDelegateRequestInterface.def(py::init())
      .def(
          "nativeData",
          [](UIDelegateRequestInterface& self) { return anyCastToPyObject(self.nativeData()); },
          py::call_guard<py::gil_scoped_release>{})
      .def("entityReferences", &UIDelegateRequestInterface::entityReferences,
           py::call_guard<py::gil_scoped_release>{})
      .def("entityTraitsDatas", &UIDelegateRequestInterface::entityTraitsDatas,
           py::call_guard<py::gil_scoped_release>{})
      .def("stateChangedCallback", &UIDelegateRequestInterface::stateChangedCallback,
           py::call_guard<py::gil_scoped_release>{});

  pyUIDelegateStateInterface.def(py::init())
      .def(
          "nativeData",
          [](UIDelegateStateInterface& self) { return anyCastToPyObject(self.nativeData()); },
          py::call_guard<py::gil_scoped_release>{})
      .def("entityReferences", &UIDelegateStateInterface::entityReferences,
           py::call_guard<py::gil_scoped_release>{})
      .def("entityTraitsDatas", &UIDelegateStateInterface::entityTraitsDatas,
           py::call_guard<py::gil_scoped_release>{})
      .def("updateRequestCallback", &UIDelegateStateInterface::updateRequestCallback,
           py::call_guard<py::gil_scoped_release>{});

  pyUIDelegateRequest
      .def(py::init(RetainCommonPyArgs::forFn<&UIDelegateRequest::make>()),
           py::arg("uiDelegateRequestInterface").none(false))
      .def(
          "nativeData",
          [](UIDelegateRequest& self) { return anyCastToPyObject(self.nativeData()); },
          py::call_guard<py::gil_scoped_release>{})
      .def("entityReferences", &UIDelegateRequest::entityReferences,
           py::call_guard<py::gil_scoped_release>{})
      .def("entityTraitsDatas", &UIDelegateRequest::entityTraitsDatas,
           py::call_guard<py::gil_scoped_release>{})
      .def("stateChangedCallback", &UIDelegateRequest::stateChangedCallback,
           py::call_guard<py::gil_scoped_release>{});

  pyUIDelegateState
      .def(py::init(RetainCommonPyArgs::forFn<&UIDelegateState::make>()),
           py::arg("uiDelegateStateInterface").none(false))
      .def(
          "nativeData", [](UIDelegateState& self) { return anyCastToPyObject(self.nativeData()); },
          py::call_guard<py::gil_scoped_release>{})
      .def("entityReferences", &UIDelegateState::entityReferences,
           py::call_guard<py::gil_scoped_release>{})
      .def("entityTraitsDatas", &UIDelegateState::entityTraitsDatas,
           py::call_guard<py::gil_scoped_release>{})
      .def("updateRequestCallback", &UIDelegateState::updateRequestCallback,
           py::call_guard<py::gil_scoped_release>{});
}
