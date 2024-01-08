// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
/**
 * Bindings used for testing errors behaviour.
 * Specifically, the conversion from cpp -> python.
 *
 * See tests/cmodule/test_errors.py
 */

#include <pybind11/pybind11.h>

#include <overrideMacros.hpp>

#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>

namespace py = pybind11;

namespace {
using openassetio::python::exceptions::CppExceptionsAndPyClassNames;

/**
 * Throw given exception type.
 *
 * Generalisation for simple exceptions that take a single string
 * message constructor argument.
 *
 * @tparam Exception Exception type to throw.
 * @param msg Message to set on exception.
 */
template <class Exception>
void throwException(const std::string& msg) {
  throw Exception{msg};
}

using openassetio::errors::BatchElementException;
/**
 * Throw a BatchElementException.
 *
 * Specialisation to handle the more complex case of
 * BatchElementException constructor.
 *
 * @param msg Message to set on BatchElementException.
 */
template <>
void throwException<BatchElementException>(const std::string& msg) {
  using openassetio::errors::BatchElementError;
  auto error = BatchElementError{BatchElementError::ErrorCode::kEntityAccessError, "errorMessage"};
  throw BatchElementException(0, std::move(error), openassetio::Str{msg});
}

/**
 * Throw an exception from the CppExceptionsAndPyClassNames list (looked
 * up by index) if the given name matches the exception's name.
 *
 * @tparam I Index in CppExceptionsAndPyClassNames of exception to
 * potentially throw.
 * @param exceptionName Name of exception to potentially throw.
 * @param msg Message to set on exception, if thrown.
 */
template <std::size_t I>
// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
void throwIfMatches(const std::string& exceptionName, const std::string& msg) {
  if (exceptionName == CppExceptionsAndPyClassNames::kClassNames[I]) {
    throwException<CppExceptionsAndPyClassNames::Exceptions<I>>(msg);
  }
}

/**
 * Throw an exception from the CppExceptionsAndPyClassNames list that
 * matches the given exception name.
 *
 * @tparam I Indices in CppExceptionsAndPyClassNames to iterate through
 * looking for a matching exception.
 * @param exceptionName Name of exception to match.
 * @param msg Message to set in thrown exception.
 */
template <std::size_t... I>
void throwMatchingException(const std::string& exceptionName, const std::string& msg,
                            [[maybe_unused]] std::index_sequence<I...> unused) {
  (throwIfMatches<I>(exceptionName, msg), ...);
}

/**
 * Throw an exception from the CppExceptionsAndPyClassNames list that
 * matches the given exception name.
 *
 * @param exceptionName Name of exception to throw.
 * @param msg Message to set in thrown exception.
 */
// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
void throwException(const std::string& exceptionName, const std::string& msg = "") {
  throwMatchingException(exceptionName, msg, CppExceptionsAndPyClassNames::kIndices);
}

/**
 * Lookup (by index) the exception to catch in the
 * CppExceptionsAndPyClassNames list and, if its name matches the given
 * @p catchExceptionName, lookup another exception to throw that matches
 * the given @p throwExceptionName, and if found, throw the exception to
 * throw and catch it as the exception to catch.
 *
 * @tparam I Index of exception in CppExceptionsAndPyClassNames to
 * attempt to catch.
 * @param throwExceptionName Name of exception type to throw.
 * @param catchExceptionName Name of exception type to catch.
 * @return `true` if the exception was thrown and caught, false (or
 * propagate exception) otherwise.
 */
template <std::size_t I>
// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
bool throwAndCatchIfMatches(const std::string& throwExceptionName,
                            const std::string& catchExceptionName) {
  if (catchExceptionName == CppExceptionsAndPyClassNames::kClassNames[I]) {
    try {
      throwException(throwExceptionName, "");
    } catch (const CppExceptionsAndPyClassNames::Exceptions<I>&) {
      return true;
    }
  }
  return false;
}
/**
 * Throw an exception (looked up by name) from the
 * CppExceptionsAndPyClassNames list and catch as another exception
 * (looked up by name) from the CppExceptionsAndPyClassNames list.
 *
 * @tparam I Indices in the CppExceptionsAndPyClassNames list to
 * iterate through searching for a matching exception to catch.
 * @param throwExceptionName Name of exception type to throw.
 * @param catchExceptionName Name of exception type to catch.
 * @return `true` if a matching exception was successfully thrown and
 * caught, `false` otherwise.
 */
template <std::size_t... I>
bool throwAndCatchMatchingException(const std::string& throwExceptionName,
                                    const std::string& catchExceptionName,
                                    [[maybe_unused]] std::index_sequence<I...> unused) {
  return (throwAndCatchIfMatches<I>(throwExceptionName, catchExceptionName) || ...);
}

/**
 * Throw an exception (looked up by name) from the
 * CppExceptionsAndPyClassNames list and catch as another exception
 * (looked up by name) from the CppExceptionsAndPyClassNames list.
 *
 * @param throwExceptionName Name of exception type to throw.
 * @param catchExceptionName Name of exception type to catch.
 * @return `true` if a matching exception was successfully thrown and
 * caught, `false` otherwise.
 */
bool throwAndCatch(const std::string& throwExceptionName, const std::string& catchExceptionName) {
  return throwAndCatchMatchingException(throwExceptionName, catchExceptionName,
                                        CppExceptionsAndPyClassNames::kIndices);
}

/**
 * Lookup (by index) an exception in the CppExceptionsAndPyClassNames
 * list and, if its name matches the given @p catchExceptionName,
 * execute a callable wrapped in a try-catch that attempts to catch the
 * exception.
 *
 * @tparam I Index in CppExceptionsAndPyClassNames list of exception to
 * catch.
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 * @return `true` if the exception was thrown and caught, false (or
 * propagate exception) otherwise.
 */
template <std::size_t I, class Fn>
bool executeFnAndCatchIfMatches(Fn&& func, const std::string& catchExceptionName) {
  if (catchExceptionName == CppExceptionsAndPyClassNames::kClassNames[I]) {
    try {
      func();
    } catch (const CppExceptionsAndPyClassNames::Exceptions<I>&) {
      return true;
    }
  }
  return false;
}

/**
 * Iterate through the CppExceptionsAndPyClassNames list, until an
 * exception is found that matches the given @p catchExceptionName, then
 * execute a callable wrapped in a try-catch that attempts to catch the
 * exception.
 *
 * @tparam I Indices in the CppExceptionsAndPyClassNames list to iterate
 * through.
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 * @return `true` if any exception matched and successfully caught the
 * exception thrown by the callable, `false` (or propagate exception)
 * otherwise.
 */
template <std::size_t... I, class Fn>
bool executeFnAndCatchMatchingException(Fn&& func, const std::string& catchExceptionName,
                                        [[maybe_unused]] std::index_sequence<I...> unused) {
  return (executeFnAndCatchIfMatches<I>(std::forward<Fn>(func), catchExceptionName) || ...);
}

/**
 * Execute a callable wrapped in a try-catch that attempts to catch the
 * exception given by name in @p catchExceptionName.
 *
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 * @return `true` if successfully executed and caught the exception
 * thrown by the callable, `false` (or propagate exception) otherwise.
 */
template <class Fn>
bool executeFnAndCatch(Fn&& func, const std::string& catchExceptionName) {
  return executeFnAndCatchMatchingException(std::forward<Fn>(func), catchExceptionName,
                                            CppExceptionsAndPyClassNames::kIndices);
}

/**
 * Lookup (by index) an exception in the CppExceptionsAndPyClassNames
 * list and, if its name matches the given @p catchExceptionName,
 * execute a callable wrapped in a try-catch that attempts to catch the
 * exception, then re-throws.
 *
 * If the callable throws any non-matching exception, then it is
 * swallowed and not allowed to propagate.
 *
 * @tparam I Index in CppExceptionsAndPyClassNames list of exception to
 * catch.
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 */
template <std::size_t I, class Fn>
void executeFnAndCatchAndRethrowIfMatches(Fn&& func, const std::string& catchExceptionName) {
  if (catchExceptionName == CppExceptionsAndPyClassNames::kClassNames[I]) {
    try {
      func();
    } catch (const CppExceptionsAndPyClassNames::Exceptions<I>&) {
      throw;
    } catch (...) {
      // Ensure error_already_set doesn't propagate and cause a false
      // positive back in the Python test case.
    }
  }
}

/**
 * Iterate through the CppExceptionsAndPyClassNames list, until an
 * exception is found that matches the given @p catchExceptionName, then
 * execute a callable wrapped in a try-catch that attempts to catch the
 * exception and re-throw it.
 *
 * If the callable throws an exception that doesn't match @p
 * catchExceptionName, then that exception is swallowed and not allowed
 * to propagate.
 *
 * @tparam I Indices in the CppExceptionsAndPyClassNames list to iterate
 * through.
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 */
template <std::size_t... I, class Fn>
void executeFnAndCatchAndRethrowMatchingException(
    Fn&& func, const std::string& catchExceptionName,
    [[maybe_unused]] std::index_sequence<I...> unused) {
  (executeFnAndCatchAndRethrowIfMatches<I>(std::forward<Fn>(func), catchExceptionName), ...);
}

/**
 * Execute a callable wrapped in a try-catch that attempts to catch the
 * exception given by name in @p catchExceptionName, then re-throws it.
 *
 * If the callable throws an exception that doesn't match @p
 * catchExceptionName, then that exception is swallowed and not allowed
 * to propagate.
 *
 * @tparam Fn Type of callable to execute.
 * @param func Callable instance to execute.
 * @param catchExceptionName Name of exception to catch.
 */
template <class Fn>
void executeFnAndCatchAndRethrow(Fn&& func, const std::string& catchExceptionName) {
  executeFnAndCatchAndRethrowMatchingException(std::forward<Fn>(func), catchExceptionName,
                                               CppExceptionsAndPyClassNames::kIndices);
}
}  // namespace

/**
 * Abstract C++ class to be implemented as a subclass in Python, which
 * is expected to implement each method such that they throw an
 * exception.
 *
 * Each method corresponds to a OpenAssetIO-customized pybind11 override
 * macro.
 */
struct ExceptionThrower {
  virtual ~ExceptionThrower() = default;
  virtual void throwFromOverride() {}
  virtual void throwFromOverridePure() = 0;
  virtual void throwFromOverrideName() {}
  virtual void throwFromOverrideArgs() {}
};

/**
 * pybind11 trampoline class for ExceptionThrower.
 *
 * Each method uses a different override macro to implement its internal
 * dispatch logic, so that all macros can be tested by calling the
 * corresponding method.
 */
struct PyExceptionThrower : ExceptionThrower {
  void throwFromOverride() override {
    OPENASSETIO_PYBIND11_OVERRIDE(void, ExceptionThrower, throwFromOverride, );
  }
  void throwFromOverridePure() override {
    OPENASSETIO_PYBIND11_OVERRIDE_PURE(void, ExceptionThrower, throwFromOverridePure, );
  }
  void throwFromOverrideName() override {
    OPENASSETIO_PYBIND11_OVERRIDE_NAME(void, ExceptionThrower, "throwFromOverrideName",
                                       throwFromOverrideName, );
  }
  void throwFromOverrideArgs() override {
    OPENASSETIO_PYBIND11_OVERRIDE_ARGS(void, ExceptionThrower, throwFromOverrideArgs, (), );
  }
};

/**
 * Functions to aid testing C++ exceptions and C++<->Python conversion.
 *
 * `throwException` takes an exception by name (matching `cls.__name__`
 * in Python) and throws it, with an optional message. This then allows
 * us to test that C++->Python exception conversion is working as
 * expected.
 *
 * `isThrownExceptionCatchableAs` is a bit of a kludge to allow us to
 * test the C++ exception hierarchy using pytest. The caller provides
 * the name of an exception to throw and the name of a (base class)
 * exception to catch. The function simply returns `True` to Python, or,
 * if the catch failed, allows the exception to propagate (failing the
 * pytest). Note that the exception hierarchy in C++ and in Python are
 * configured independently, so testing one does not test the other.
 *
 * `isPythonExceptionCatchableAs` instructs Python to throw an exception
 * and ensures it can be caught as the given C++ exception. It takes an
 * abstract `ExceptionThrower` instance, whose concrete implementation
 * is in Python. All methods of the `ExceptionThrower` object are called
 * and their results combined to ensure that all override macros
 * implement Python->C++ exception translation. Note that the GIL is
 * released deliberately in order to better simulate the situation in
 * OpenAssetIO Python bindings.
 *
 * `throwPythonExceptionCatchAsCppExceptionAndRethrow` instructs Python
 * to throw an exception and ensures it can be caught as the given C++
 * exception, and then re-throws the C++ exception, so that it can be
 * caught again in Python as a Python exception. This is technically
 * not necessary to test, since both C++->Python and Python->C++
 * exception translation are already tested independently, but it gives
 * some additional confidence. Note that the GIL is released
 * deliberately in order to better simulate the situation in OpenAssetIO
 * Python bindings.
 *
 * `throwPythonExceptionAndCatchAsStdException` instructs Python to
 * throw an exception and attempts to catch it as a `std::exception` and
 * a `std::runtime_error`. This is a regression test against RTTI issues
 * between hybrid pybind11 and OpenAssetIO exceptions, which have a
 * common STL base class so must be composed with care (i.e. avoid
 * multiple inheritance).
 */
void registerExceptionThrower(py::module_& mod) {
  mod.def("throwException", [](const std::string& exceptionName, const std::string& msgData) {
    throwException(exceptionName, msgData);
  });

  mod.def(
      "isThrownExceptionCatchableAs",
      [](const std::string& throwExceptionName, const std::string& catchExceptionName) {
        return throwAndCatch(throwExceptionName, catchExceptionName);
      },
      py::arg("throwExceptionName"), py::arg("catchExceptionName"));

  mod.def(
      "isPythonExceptionCatchableAs",
      [](ExceptionThrower& exceptionThrower, const std::string& catchExceptionName) {
        return executeFnAndCatch([&] { exceptionThrower.throwFromOverride(); },
                                 catchExceptionName) &&
               executeFnAndCatch([&] { exceptionThrower.throwFromOverrideArgs(); },
                                 catchExceptionName) &&
               executeFnAndCatch([&] { exceptionThrower.throwFromOverrideName(); },
                                 catchExceptionName) &&
               executeFnAndCatch([&] { exceptionThrower.throwFromOverridePure(); },
                                 catchExceptionName);
      },
      py::arg("exceptionThrower"), py::arg("catchExceptionName"),
      py::call_guard<py::gil_scoped_release>{});

  mod.def(
      "throwPythonExceptionCatchAsCppExceptionAndRethrow",
      [](ExceptionThrower& exceptionThrower, const std::string& catchExceptionName) {
        // Arbitrarily use `throwFromOverride`, trusting that the
        // underlying implementation (i.e.
        // `decorateWithExceptionConverter`) is the same for all macros.
        executeFnAndCatchAndRethrow([&] { exceptionThrower.throwFromOverride(); },
                                    catchExceptionName);
      },
      py::arg("exceptionThrower"), py::arg("catchExceptionName"),
      py::call_guard<py::gil_scoped_release>{});

  mod.def(
      "throwPythonExceptionAndCatchAsStdException",
      [](ExceptionThrower& exceptionThrower) {
        // If we fail to catch in either of the following try-catch
        // blocks, the exception will propagate, implicitly failing the
        // pytest test in Python.
        try {
          exceptionThrower.throwFromOverride();
        } catch (const std::exception&) {  // NOLINT(*-empty-catch)
        }
        try {
          exceptionThrower.throwFromOverride();
        } catch (const std::runtime_error&) {  // NOLINT(*-empty-catch)
        }
      },
      py::arg("exceptionThrower"), py::call_guard<py::gil_scoped_release>{});

  py::class_<ExceptionThrower, PyExceptionThrower>{mod, "ExceptionThrower"}
      .def(py::init<>())
      .def("throwFromOverride", &ExceptionThrower::throwFromOverride)
      .def("throwFromOverridePure", &ExceptionThrower::throwFromOverridePure)
      .def("throwFromOverrideName", &ExceptionThrower::throwFromOverrideName)
      .def("throwFromOverrideArgs", &ExceptionThrower::throwFromOverrideArgs);
}
