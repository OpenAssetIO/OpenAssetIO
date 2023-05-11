// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/python/converter/converters.hpp>

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

// using openassetio::hostApi::Manager;
// using openassetio::hostApi::ManagerPtr;

template <typename T>
PyObject* castToPyObject(const T& objectPtr) {
  if (objectPtr == nullptr) {
    throw std::invalid_argument("objectPtr cannot be null");
  }

  return py::cast(objectPtr).release().ptr();
}

template <typename T>
typename T::Ptr castFromPyObject(PyObject* pyObject) {
  if (pyObject == nullptr) {
    throw std::invalid_argument("pyObject cannot be null");
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
    throw std::invalid_argument(std::string("Could not cast pyObject to type ") +
                                typeid(T).name());
  }
}

// To/from explicit specialization convenience.
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
