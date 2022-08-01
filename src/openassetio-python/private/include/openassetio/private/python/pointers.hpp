// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once
#include <memory>
#include <utility>

#include <pybind11/pybind11.h>

#include <openassetio/export.h>

namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace python::pointers {
/**
 * Get a shared_ptr-compatible smart pointer that controls the lifetime
 * of a Python object reference, but dereferences to a C++ object.
 *
 * This function can be used to create a shared_ptr that increments
 * the Python object's refcount and so keeps it alive. Destruction of
 * the shared_ptr then decrements the Python object's refcount.
 *
 * This is especially useful when the Python object is linked to the C++
 * object via a pybind11 shared_ptr holder, so that when the Python
 * refcount reaches zero (and hence the Python object is destroyed), the
 * shared_ptr holder refcount is decremented.
 *
 * In this way the lifetimes of the two shared_ptr "endpoints" are
 * linked by the Python object refcount.
 *
 * @see PyRetainingSharedPtr
 * @see createPythonPluginSystemManagerImplementationFactory
 *
 * @tparam Ptr Type of smart pointer (shared_ptr compatible).
 * @param pyInstance Python object whose lifetime will be modified..
 * @param cppInstancePtr Pointer to C++ instance that the returned
 * pointer should dereference to.
 * @return A smart pointer that dereferences to a C++ object, but
 * which controls the lifetime of a Python object reference.
 */
template <typename Ptr>
Ptr createPyRetainingPtr(const py::object& pyInstance,
                         typename Ptr::element_type* cppInstancePtr) {
  // Use a shared_ptr to bump the PyObject refcount, and decrement
  // again when the shared_ptr chain is cleaned up. This may result in
  // destruction of the PyObject and hence decrementing the refcount
  // of the original shared_ptr holder stored on the PyObject.
  auto pyInstancePtr =
      std::shared_ptr<py::object>{new py::object{pyInstance}, [](py::object* pyObjectPtr) {
                                    // Acquire the GIL, in case deleter
                                    // runs in a non-Python thread.
                                    py::gil_scoped_acquire gil;
                                    delete pyObjectPtr;
                                  }};

  // We use the shared_ptr aliasing constructor to track the lifetime of
  // the py::object, but dereference to the C++ instance. When this
  // shared_ptr (and any other shared_ptrs copy-constructed from it) is
  // destroyed, then the PyObject refcount will be decremented (see
  // above), potentially resulting in destruction of the PyObject and
  // hence decrementing the originating C++ shared_ptr refcount.
  return Ptr{pyInstancePtr, cppInstancePtr};
}
}  // namespace python::pointers
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
