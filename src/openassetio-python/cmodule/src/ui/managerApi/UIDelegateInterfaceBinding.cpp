// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

// NOLINTBEGIN(*-include-cleaner): Needed by pybind11.
#include <openassetio/managerApi/HostSession.hpp>
// NOLINTEND(*-include-cleaner)

#include "../../_openassetio.hpp"
#include "../../overrideMacros.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::managerApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyUIDelegateInterface : UIDelegateInterface {
  using UIDelegateInterface::UIDelegateInterface;

  [[nodiscard]] Identifier identifier() const override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(Identifier, UIDelegateInterface, identifier, /* no args */);
  }

  [[nodiscard]] Str displayName() const override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(Str, UIDelegateInterface, displayName, /* no args */);
  }

  [[nodiscard]] InfoDictionary info() override {
    OPENASSETIO_PYBIND11_OVERRIDE(InfoDictionary, UIDelegateInterface, info, /* no args */);
  }

  [[nodiscard]] InfoDictionary settings(const HostSessionPtr& hostSession) override {
    OPENASSETIO_PYBIND11_OVERRIDE(InfoDictionary, UIDelegateInterface, settings, hostSession);
  }

  void initialize(InfoDictionary uiDelegateSettings, const HostSessionPtr& hostSession) override {
    OPENASSETIO_PYBIND11_OVERRIDE(void, UIDelegateInterface, initialize,
                                  std::move(uiDelegateSettings), hostSession);
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
      .def("displayName", &UIDelegateInterface::displayName,
           py::call_guard<py::gil_scoped_release>{})
      .def("info", &UIDelegateInterface::info, py::call_guard<py::gil_scoped_release>{})
      .def("settings", &UIDelegateInterface::settings, py::arg("hostSession").none(false),
           py::call_guard<py::gil_scoped_release>{})
      .def("initialize", &UIDelegateInterface::initialize, py::arg("managerSettings"),
           py::arg("hostSession").none(false), py::call_guard<py::gil_scoped_release>{});
}
