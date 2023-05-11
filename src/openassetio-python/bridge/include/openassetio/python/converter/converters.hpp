// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <Python.h>
#include <openassetio/export.h>
#include <openassetio/python/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Utilities for bridging from C++ to Python.
 */
namespace python {  // NOLINT(modernize-concat-nested-namespaces)
/// Host-side utilities for bridging from C++ to Python.
namespace converter {
/**
 * Casts a C++ API object to the equivalent Python Object.
 *
 * These template is explicitly instantiated to only the OpenAssetIO
 * types, and is not intended to be a generic converter.
 *
 * @note The purpose of this function is to hide the pybind11
 * dependency, allowing consumers to retrieve a Python object without
 * having to have pybind in their build stack. A pybind cast is done
 * behind the scenes, returning the released ptr from that.
 *
 * Using this function does not require specifying the template
 * argument, as it can be deduced from \p objectPtr.
 *
 * @throws std::invalid_argument if the input is null.
 *
 * @param objectPtr An OpenAssetIO pointer type, (eg, @ref ManagerPtr).
 * The returned pointer takes shared ownership of the input
 * \p objectPtr, and will keep the c++ instance alive until the
 * `PyObject` is destroyed.
 *
 * @return A `PyObject` pointer to an object of the python api type
 * associated with the c++ api object provided.
 * The pointer is not an RAII type, has a reference count of 1, and
 * must be destroyed manually via `Py_DECREF` or similar mechanisms.
 */
template <typename T>
OPENASSETIO_PYTHON_BRIDGE_EXPORT PyObject* castToPyObject(const T& objectPtr);

/**
 * Casts a Python object to the equivalent C++ Api Object.
 *
 * This template is explicitly instantiated to only the OpenAssetIO
 * types, and is not intended to be a generic converter.
 *
 * This function will increase the reference count of the provided
 * Python object by one for the lifetime of the returned C++ object.
 * When the returned C++ object falls out of scope or is otherwise
 * cleaned up, the Python object will have its reference count reduced
 * by one, potentially invoking cleanup.
 *
 * Using this function requires specifying the template argument of
 * the C++ API type equivalent to the type of the object referred to by
 * the \p pyObject pointer.
 *
 * ~~~~~{.cpp}
 * ManagerPtr manager = castFromPyObject<Manager>(pyManager);
 * ~~~~
 *
 *  If the types of the template argument and the \p pyObject are not
 * equivalent, an exception will be thrown due to inability to perform
 * the cast.
 *
 * @throws std::invalid_argument if the function fails due to inability
 * to cast between types, or if the input is null.
 *
 * @note The purpose of this function is to hide the pybind11
 * dependency, allowing consumers to retrieve a Python object without
 * having to have pybind in their build stack. A pybind cast is done
 * behind the scenes, returning the C++ object pointer from that.
 *
 * @param pyObject A `PyObject` pointer to a python object that must be
 * of equivalent type to the template argument.
 *
 * @return An OpenAssetIO pointer to a C++ API object cast from the
 * provided \p pyObject. This pointer is created via @ref
 * PyRetainingSharedPtr, and thus will increment the reference count of
 * the Python object whilst it remains in scope, and decrement it once
 * it leaves scope.
 */
template <typename T>
OPENASSETIO_PYTHON_BRIDGE_EXPORT typename T::Ptr castFromPyObject(PyObject* pyObject);

}  // namespace converter
}  // namespace python
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
