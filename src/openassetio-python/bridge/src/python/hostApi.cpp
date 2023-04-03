// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/python/hostApi.hpp>

#include <memory>

#include <pybind11/embed.h>

#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
// Private headers
#include <openassetio/private/python/pointers.hpp>

namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::hostApi {

using openassetio::hostApi::ManagerImplementationFactoryInterface;
using openassetio::hostApi::ManagerImplementationFactoryInterfacePtr;

ManagerImplementationFactoryInterfacePtr createPythonPluginSystemManagerImplementationFactory(
    log::LoggerInterfacePtr logger) {  // NOLINT(performance-unnecessary-value-param)
  // Caller might not hold the GIL, which is required for `import`s.
  const py::gil_scoped_acquire gil{};

  // Get Python class.
  const py::object pyClass =
      py::module_::import(
          "openassetio.pluginSystem.PythonPluginSystemManagerImplementationFactory")
          .attr("PythonPluginSystemManagerImplementationFactory");

  // Instantiate Python object.
  const py::object pyInstance = pyClass(std::move(logger));

  // Extract the underlying C++ base class pointer.
  auto* cppInstancePtr = py::cast<ManagerImplementationFactoryInterface*>(pyInstance);

  // Use aliasing constructor, linking Python instance and C++ instance
  // lifetimes via PyObject refcount.
  return pointers::createPyRetainingPtr<ManagerImplementationFactoryInterfacePtr>(pyInstance,
                                                                                  cppInstancePtr);
}
}  // namespace python::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
