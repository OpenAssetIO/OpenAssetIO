// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/python/converter.hpp>

#include <pybind11/embed.h>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/log/SeverityFilter.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>

// Private headers
#include <openassetio/private/python/pointers.hpp>

namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::converter {

template <typename T>
PyObject* castToPyObject(const T& objectPtr) {
  // Stash the errors for restoring after cast.
  // An error_scope calls PyErr_Fetch (which clears the active error),
  // and stashes them, restoring the error state when it falls out of
  // scope
  const py::error_scope previousErrorState;

  py::object pybindObj = py::cast(objectPtr);

  // Check to see if the py::cast has spawned a python error
  // We use another error_scope here for convenience of access, relying
  // on the fact that the original error scope will be destructed last,
  // resetting to the initial error.
  const py::error_scope castErrorState;

  if (castErrorState.value != nullptr) {
    throw std::runtime_error(py::str(castErrorState.value));
  }

  // `release()` to avoid decrementing the PyObject refcount on leaving
  // this function. We explicitly want +1 refcount.
  return pybindObj.release().ptr();
}

template <typename T>
typename T::Ptr castFromPyObject(PyObject* pyObject) {
  if (pyObject == nullptr) {
    throw std::invalid_argument(
        "Attempting to cast a nullptr PyObject in "
        "openassetio::python::converter::castFromPyObject");
  }

  // get Python object.
  const auto pyInstance = py::reinterpret_borrow<py::object>(pyObject);

  try {
    // Extract the underlying C++ base class pointer.
    auto* cppInstancePtr = py::cast<T*>(pyInstance);

    // Use aliasing constructor, linking Python instance and C++ instance
    // lifetimes via PyObject refcount.
    return pointers::createPyRetainingPtr<typename T::Ptr>(pyInstance, cppInstancePtr);
  } catch (const py::cast_error& castError) {
    // Rethrow here to avoid bleeding pybind exception dependencies.
    throw std::invalid_argument(castError.what());
  }
}

// To/from explicit specialization convenience.
// As these specializations are being used across library boundaries,
// we must export them to prevent undefined-symbol link errors.
#define OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(Class)                          \
  template OPENASSETIO_PYTHON_BRIDGE_EXPORT PyObject* castToPyObject<Class::Ptr>( \
      const Class::Ptr&);                                                         \
  template OPENASSETIO_PYTHON_BRIDGE_EXPORT Class::Ptr castFromPyObject<Class>(PyObject*);

OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(openassetio::Context)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(openassetio::TraitsData)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(hostApi::HostInterface)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(hostApi::Manager)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(hostApi::ManagerFactory)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(hostApi::ManagerImplementationFactoryInterface)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(log::ConsoleLogger)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(log::LoggerInterface)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(log::SeverityFilter)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(managerApi::Host)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(managerApi::HostSession)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(managerApi::ManagerInterface)
OPENASSETIO_SPECIALIZE_PYTHON_CONVERSIONS(managerApi::ManagerStateBase)

}  // namespace python::converter
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
