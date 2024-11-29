// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <Python.h>

#include <openassetio/export.h>
#include <openassetio/python/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Converter functionality for going between C++ and CPython objects.
 */
namespace python::converter {
/**
 * Casts a C++ API object to the equivalent Python object.
 *
 * This template is explicitly instantiated to only the OpenAssetIO
 * types, and is not intended to be a generic converter.
 *
 * The purpose of this function is to provide a Python/C++ conversion
 * without requiring/exposing a particular CPython binding library
 * implementation.
 *
 * The returned `PyObject` owns a hidden reference to the input
 * `shared_ptr`, ensuring it is kept alive. The reference will be
 * released when the `PyObject` is destroyed.
 *
 * @note This function does not acquire the GIL.
 *
 * @warning A Python environment, with `openassetio` imported, must be
 *          available in order to use this function.
 *
 * @param objectPtr A non-const OpenAssetIO pointer type, (eg, @needsref
 * ManagerPtr). The returned `PyObject` takes shared ownership of this
 * input \p objectPtr, and will keep the C++ instance alive until the
 * `PyObject` is destroyed.
 * This parameter must be the non-const OpenAssetIO pointer type as
 * casting to python erases constness.
 *
 * @return A `PyObject` pointer to an object of the Python API type
 * associated with the C++ API object provided. The reference count of
 * the `PyObject` will be incremented, and must be decremented by the
 * caller when done.
 *
 * @throws errors.InputValidationException if the cast fails.
 */
template <typename T>
OPENASSETIO_PYTHON_BRIDGE_EXPORT PyObject* castToPyObject(const T& objectPtr);

/**
 * Casts a Python object to the equivalent C++ API object.
 *
 * This template is explicitly instantiated to only the OpenAssetIO
 * types, and is not intended to be a generic converter.
 *
 * The purpose of this function is to provide a Python/C++ conversion
 * without requiring/exposing a particular CPython binding library
 * implementation.
 *
 * The returned `shared_ptr` owns a hidden reference to the input
 * `PyObject`, ensuring it is kept alive. The reference will be released
 * when the `shared_ptr` is destroyed.
 *
 * Using this function requires specifying the template argument of
 * the C++ API type equivalent to the type of the object referred to by
 * the \p pyObject pointer.
 *
 * @code{.cpp}
 * ManagerPtr manager = castFromPyObject<Manager>(pyManager);
 * @endcode
 *
 *
 * If the types of the template argument and the \p pyObject are not
 * equivalent, an exception will be thrown due to inability to perform
 * the cast.
 *
 * @note This function does not acquire the GIL.
 *
 * @warning A Python environment, with `openassetio` imported, must be
 *          available in order to use this function.
 *
 * @param pyObject A `PyObject` pointer to a Python object that must be
 * of equivalent type to the template argument.
 *
 * @return An OpenAssetIO pointer to a C++ API object cast from the
 * provided \p pyObject. The lifetime of the PyObject will be extended
 * to at least the lifetime of the returned `shared_ptr`.
 *
 * @throws errors.InputValidationException if the function fails due to
 * inability to cast between types, or if the input is null.
 */
template <typename T>
OPENASSETIO_PYTHON_BRIDGE_EXPORT typename T::Ptr castFromPyObject(PyObject* pyObject);

}  // namespace python::converter
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
