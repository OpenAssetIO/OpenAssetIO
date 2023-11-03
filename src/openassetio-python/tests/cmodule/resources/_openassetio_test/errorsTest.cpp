// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
/**
 * Bindings used for testing errors behaviour.
 * Specifically, the conversion from cpp -> python.
 *
 * See tests/cmodule/test_errors.py
 */

#include <pybind11/pybind11.h>

#include <_openassetio.hpp>
// Frustratingly, must include .cpp since we need private symbols.
#include <errors/exceptionsBinding.cpp>  // NOLINT

#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>
namespace py = pybind11;

namespace {

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

}  // namespace

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
}
