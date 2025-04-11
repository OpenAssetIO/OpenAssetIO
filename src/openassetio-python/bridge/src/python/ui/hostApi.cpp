// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <openassetio/python/ui/hostApi.hpp>

#include <utility>

#include <pybind11/embed.h>

#include <openassetio/export.h>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
// Private headers
#include <openassetio/private/python/pointers.hpp>

namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::ui::hostApi {

using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterface;
using openassetio::ui::hostApi::UIDelegateImplementationFactoryInterfacePtr;

UIDelegateImplementationFactoryInterfacePtr
createPythonPluginSystemUIDelegateImplementationFactory(
    log::LoggerInterfacePtr logger) {  // NOLINT(performance-unnecessary-value-param)
  // Caller might not hold the GIL, which is required for `import`s.
  const py::gil_scoped_acquire gil{};

  // Get Python class.
  const py::object pyClass =
      py::module_::import(
          "openassetio.ui.pluginSystem.PythonPluginSystemUIDelegateImplementationFactory")
          .attr("PythonPluginSystemUIDelegateImplementationFactory");

  // Instantiate Python object.
  const py::object pyInstance = pyClass(std::move(logger));

  // Extract the underlying C++ base class pointer.
  auto* cppInstancePtr = py::cast<UIDelegateImplementationFactoryInterface*>(pyInstance);

  // Use aliasing constructor, linking Python instance and C++ instance
  // lifetimes via PyObject refcount.
  return pointers::createPyRetainingPtr<UIDelegateImplementationFactoryInterfacePtr>(
      pyInstance, cppInstancePtr);
}
}  // namespace python::ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
