// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include <cassert>
#include <cstddef>
#include <exception>
#include <string>  // NOLINT(misc-include-cleaner): used in assert().
#include <string_view>
#include <unordered_map>
#include <utility>

#include <pybind11/eval.h>
#include <pybind11/pybind11.h>

#include <openassetio/errors/exceptions.hpp>

#include "../_openassetio.hpp"
#include "./exceptionsConverter.hpp"

namespace {
using openassetio::errors::BatchElementException;
using openassetio::errors::ConfigurationException;
using openassetio::errors::InputValidationException;
using openassetio::errors::NotImplementedException;
using openassetio::errors::OpenAssetIOException;
using openassetio::errors::UnhandledException;

/**
 * @section topy Conversion from C++ exception to Python exception.
 *
 * @{
 */

/**
 * Set the current Python exception in this thread.
 *
 * @tparam Exception C++ exception type.
 * @param exception C++ exception instance.
 * @param pyClassName Python exception class name to look up in @p
 * pyModule.
 */
template <class Exception>
void setPyException(const Exception &exception, const std::string_view pyClassName) {
  // Python "raise from" logic. See pybind11::raise_from. We need this
  // to handle the case of a C++ exception being translated when the
  // Python error indicator is already set for a different exception.
  // This can't happen easily - most likely a C++ function triggered a
  // CPython error state before throwing its own C++ exception.
  auto fromExcVal = []() -> PyObject * {
    if (!PyErr_Occurred()) {
      return nullptr;
    }
    PyObject *excVal = nullptr;
    PyObject *excType = nullptr;
    PyObject *excTraceback = nullptr;
    // Fetch (and clear) the original "from" exception. Note that if we
    // don't clear it, the `import` below will cause a fatal Python
    // error.
    PyErr_Fetch(&excType, &excVal, &excTraceback);
    PyErr_NormalizeException(&excType, &excVal, &excTraceback);
    if (excTraceback != nullptr) {
      PyException_SetTraceback(excVal, excTraceback);
      Py_DECREF(excTraceback);
    }
    Py_DECREF(excType);
    return excVal;
  }();

  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)`
  assert(!PyErr_Occurred());

  // Find the Python exception type corresponding to the given C++
  // exception, and construct an instance.
  // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
  const py::module_ pyModule = py::module_::import(kErrorsModuleName.data());
  // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
  const py::object pyClass = pyModule.attr(pyClassName.data());
  const py::object pyInstance = [&] {
    if constexpr (std::is_same_v<Exception, BatchElementException>) {
      return pyClass(exception.index, exception.error, exception.what());
    } else {
      return pyClass(exception.what());
    }
  }();

  // Set the error indicator to our converted C++->Python exception.
  PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());

  // Set the __cause__ of our new exception if raising from a previous
  // exception.
  if (fromExcVal != nullptr) {
    PyObject *excVal = nullptr;
    PyObject *excType = nullptr;
    PyObject *excTraceback = nullptr;
    PyErr_Fetch(&excType, &excVal, &excTraceback);
    PyErr_NormalizeException(&excType, &excVal, &excTraceback);
    Py_INCREF(fromExcVal);  // Bump to own two references, stolen by SetCause and SetContext.
    PyException_SetCause(excVal, fromExcVal);
    PyException_SetContext(excVal, fromExcVal);
    PyErr_Restore(excType, excVal, excTraceback);
  }
}

/**
 * Recursive try-catch.
 *
 * Recurse to next nested try-catch block, attempt to catch given
 * exception type (looked up by index) and, if caught, set the
 * corresponding Python exception.
 *
 * Recursive termination condition occurs at 0th index, whereupon the
 * given `exception_ptr` is rethrown and propagates up the nested
 * try-catch blocks until it is caught.
 *
 * If the exception is a `HybridException` type, i.e. was originally a
 * Python exception that has propagated through C++ and is now
 * propagating back out to Python, then rethrow the original Python
 * error. Otherwise, construct a new Python exception from the C++
 * exception.
 *
 * @tparam I Index of exception type to catch in
 * CppExceptionsAndPyClassNames list.
 * @param pexc C++ exception to rethrow.
 */
template <std::size_t I>
void tryCatch(std::exception_ptr pexc) {
  try {
    if constexpr (I == 0) {
      std::rethrow_exception(std::move(pexc));
    } else {
      tryCatch<I - 1>(std::move(pexc));
    }
  } catch (const HybridException<CppExceptionsAndPyClassNames::Exceptions<I>> &cppExc) {
    throw cppExc.originalPyExc;
  } catch (const CppExceptionsAndPyClassNames::Exceptions<I> &cppExc) {
    setPyException(cppExc, CppExceptionsAndPyClassNames::kClassNames[I]);
  }
}

/// Mapping of Python class name to Python class object.
using PyObjectByName = std::unordered_map<std::string_view, const py::object>;

/**
 * For a given C++ exception, find the Python class name of its base
 * class in the CppExceptionsAndPyClassNames list.
 *
 * Recursively iterates through the CppExceptionsAndPyClassNames list
 * searching for the first base class of @p Exception and returns the
 * Python class name of it. This works since the list must be sorted
 * from most-derived to least-derived.
 *
 * @tparam Exception Exception to find base class for.
 * @tparam I Current index in the CppExceptionsAndPyClassNames list to
 * consider.
 * @tparam J Remaining indices in the CppExceptionsAndPyClassNames list
 * to consider if class at @p I is not a base class.
 * @return Python class name corresponding to the most-derived base
 * class of @p Exception.
 */
template <class Exception, std::size_t I, std::size_t... J>
constexpr std::string_view findPyClassNameOfCppBaseClass(
    [[maybe_unused]] std::index_sequence<I, J...> unused) {
  using CandidateBase = CppExceptionsAndPyClassNames::Exceptions<I>;

  if constexpr (std::is_base_of_v<CandidateBase, Exception> &&
                !std::is_same_v<CandidateBase, Exception>) {
    return CppExceptionsAndPyClassNames::kClassNames[I];
  } else {
    return findPyClassNameOfCppBaseClass<Exception>(std::index_sequence<J...>{});
  }
}

/**
 * Register a new Python exception.
 *
 * @tparam Exception Corresponding C++ exception type.
 * @param pyClassName Python exception class name to register.
 * @param mod Python module to hold new Python exception class.
 * @param registeredExceptions Previously registered exceptions, to use
 * when looking up Python base class to inherit from, and to add this
 * exception to once registered.
 */
template <class Exception>
void registerPyExceptionClass(const std::string_view pyClassName, const py::module_ &mod,
                              PyObjectByName &registeredExceptions) {
  // Register the exception via pybind11.
  py::object pyExc = [&] {
    if constexpr (std::is_same_v<Exception, OpenAssetIOException>) {
      // Specialisation for OpenAssetIOException root base class, which
      // inherits from built-in Python RuntimeError exception.
      // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
      return py::exception<void /* unused */>{mod, pyClassName.data(), PyExc_RuntimeError};
    } else if constexpr (std::is_same_v<Exception, BatchElementException>) {
      // Specialisation for BatchElementException, which must be handled
      // as a special case due to its non-standard constructor
      // signature.
      //
      // pybind11 has very limited support for custom exception types.
      // This is a well-known tricky issue and is apparently not on the
      // roadmap to fix. The only direct support is for an exception
      // type that takes a single string parameter (message). However,
      // we need `index` and `error` parameters to mirror the C++
      // BatchElementException.
      //
      // A way forward is provided by the sketch in:
      // https://github.com/pybind/pybind11/issues/1281#issuecomment-1375950333
      //
      // We execute a Python string literal to create our exception
      // type. The `globals` and `locals` dict parameters dictate the
      // scope of execution, so we use this to ensure the definition is
      // scoped to the correct Python module.
      py::exec(R"pybind(
class BatchElementException(OpenAssetIOException):
    def __init__(self, index: int, error, message: str):
        self.index = index
        self.error = error
        self.message = message
        super().__init__(message))pybind",
               mod.attr("__dict__"), mod.attr("__dict__"));

      // Retrieve a handle to the exception type just created by executing
      // the string literal above.
      return mod.attr("BatchElementException");

    } else {
      // General case of a simple exception (only takes a single string
      // constructor argument) with an OpenAssetIOException-derived base
      // class.

      // Locate the Python base class name. Assumes the Python class
      // hierarchy mirrors C++.
      static constexpr std::string_view kPyBaseClassName =
          findPyClassNameOfCppBaseClass<Exception>(CppExceptionsAndPyClassNames::kIndices);
      // Look up the Python base class object.
      const py::object &pyBaseClass = registeredExceptions.at(kPyBaseClassName);
      // Register the exception, inheriting from looked-up base.
      // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
      return py::exception<void /* unused */>{mod, pyClassName.data(), pyBaseClass};
    }
  }();
  // Ensure this class can be used in subsequent base class lookups, in
  // case this class is a base of another.
  registeredExceptions.insert({pyClassName, std::move(pyExc)});
}

/**
 * Register Python exceptions corresponding to C++ exceptions in the
 * CppExceptionsAndPyClassNames list (looked up by indices).
 *
 * @tparam I Indices of exceptions in CppExceptionsAndPyClassNames.
 * @param mod Python module to hold new Python exception classes.
 */
template <std::size_t... I>
void registerPyExceptionClasses(const py::module &mod,
                                [[maybe_unused]] std::index_sequence<I...> unused) {
  // Temporarily keep track of registered exceptions as we iterate
  // through, so subclasses can retrieve base class objects to derive
  // from.
  PyObjectByName registeredExceptions;
  // Note: must reverse order of iteration through
  // CppExceptionsAndPyClassNames, since base classes must be registered
  // first so that they're subsequently available in
  // registeredExceptions.
  (registerPyExceptionClass<CppExceptionsAndPyClassNames::Exceptions<sizeof...(I) - I - 1>>(
       CppExceptionsAndPyClassNames::kClassNames[sizeof...(I) - I - 1], mod, registeredExceptions),
   ...);
}
}  // namespace

/**
 * Register Python exceptions with pybind11.
 *
 * @param mod Python module to hold new Python exception classes.
 */
void registerExceptions(const py::module &mod) {
  // Ensure module name matches what we expect, since it must be
  // imported by name in `setPyException`.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(mod.attr("__name__").cast<std::string>() == kErrorsModuleName);
  // Register new Python exception types. Note that this is not
  // sufficient to cause C++ exceptions to be translated. See
  // `register_exception_translator` below.
  registerPyExceptionClasses(mod, CppExceptionsAndPyClassNames::kIndices);

  // Register a function that will translate our C++ exceptions to the
  // appropriate Python exception type.
  //
  // Note that capturing lambdas are not allowed here, so we must
  // `import` the module containing the exceptions in the body of the
  // function (see setPyException).
  py::register_exception_translator([](std::exception_ptr pexc) {
    if (!pexc) {
      return;
    }
    // Handle the different possible C++ exceptions, creating the
    // corresponding Python exception and setting it as the active
    // exception in this thread.
    tryCatch<CppExceptionsAndPyClassNames::kSize - 1>(std::move(pexc));
  });
}

/**
 * @}
 */
