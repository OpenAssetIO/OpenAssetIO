// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
#include <array>
#include <cstddef>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>

#include <pybind11/pybind11.h>

#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>

/**
 * @section list List of exceptions.
 *
 * @{
 */

/**
 * Container for a list of types and their corresponding string
 * identifiers.
 *
 * @tparam Type List of types.
 */
template <class... Type>
struct TypesAndIds {
  static constexpr std::size_t kSize = sizeof...(Type);
  using Types = std::tuple<Type...>;
  const std::array<std::string_view, kSize> ids;
};

/**
 * Exhaustive list of all OpenAssetIO-specific C++ exception types and
 * their corresponding Python class names.
 *
 * Note base classes must come _after_ subclasses (asserted at
 * compile-time, below). This is so that try-catch blocks can be ordered
 * such that more-derived exceptions come before less-derived. See
 * `tryCatch`.
 */
constexpr auto kCppExceptionsAndPyClassNames = TypesAndIds<
    openassetio::errors::BatchElementException, openassetio::errors::NotImplementedException,
    openassetio::errors::UnhandledException, openassetio::errors::ConfigurationException,
    openassetio::errors::InputValidationException, openassetio::errors::OpenAssetIOException>{
    "BatchElementException",  "NotImplementedException",  "UnhandledException",
    "ConfigurationException", "InputValidationException", "OpenAssetIOException"};

/**
 * Convenience struct deriving compile-time properties from the above
 * list of OpenAssetIO-specific exception class types and names.
 *
 * In particular there are two lists, such that given a single index,
 * the C++ exception class or the Python class name can be queried at
 * compile time.
 */
struct CppExceptionsAndPyClassNames {
  using Type = decltype(kCppExceptionsAndPyClassNames);
  /// "Array" of C++ exception classes.
  template <std::size_t I>
  using Exceptions = std::tuple_element_t<I, typename Type::Types>;
  /// Array of Python exception class names.
  static constexpr std::array kClassNames = kCppExceptionsAndPyClassNames.ids;
  /// Total number of exceptions in the list(s).
  static constexpr std::size_t kSize = Type::kSize;
  /**
   * Convenience for a sequence of indices, used for compile-time
   * iteration over C++ exception classes.
   */
  static constexpr auto kIndices = std::make_index_sequence<kSize>{};
};

/**
 * @}
 */

/**
 * @section tocpp Conversion from Python exception to C++ exception.
 *
 * @{
 */

/**
 * Hybrid of OpenAssetIO and pybind11 exception class.
 *
 * This template class inherits from its template argument, allowing it
 * to be caught transparently as the wrapped C++ exception type.
 *
 * The corresponding Python exception (as reflected by a pybind11
 * `error_already_set` object), is stored for potential recall if this
 * C++ exception propagates back out to Python - see
 * `registerExceptions`.
 *
 * Generalisation assuming that the given exception type is a simple
 * exception that takes a string message as its only constructor
 * argument.
 *
 * @tparam CppException C++ exception type corresponding to given
 * Python exception.
 */
template <class CppException>
struct HybridException : CppException {
  explicit HybridException(const pybind11::error_already_set &pyExc)
      : CppException{pyExc.what()}, originalPyExc{pyExc} {}

  pybind11::error_already_set originalPyExc;
};

/**
 * Hybrid of OpenAssetIO and pybind11 exception class.
 *
 * Specialisation for more complex case of BatchElementException. See
 * generalisation, above, for more details.
 */
template <>
struct HybridException<openassetio::errors::BatchElementException>
    : openassetio::errors::BatchElementException {
  explicit HybridException(const pybind11::error_already_set &pyExc)
      : BatchElementException{pybind11::cast<std::size_t>(pyExc.value().attr("index")),
                              pybind11::cast<openassetio::errors::BatchElementError>(
                                  pyExc.value().attr("error")),
                              pyExc.what()},
        originalPyExc{pyExc} {}

  pybind11::error_already_set originalPyExc;
};

/**
 * Throw a HybridException if the given Python class name matches the
 * given expected Python class name corresponding to the given C++
 * exception type.
 *
 * @tparam Exception C++ exception to wrap in a HybridException.
 * @param expectedPyExcName Python exception class name corresponding
 * to @p Exception class.
 * @param thrownPyExc pybind11-wrapped Python exception to potentially
 * wrap in a HybridException.
 * @param thrownPyExcName Python exception class name of @p thrownPyExc
 * to test against @p expectedPyExcName.
 */
template <class Exception>
void throwHybridExceptionIfMatches(const std::string_view expectedPyExcName,
                                   const pybind11::error_already_set &thrownPyExc,
                                   const std::string_view thrownPyExcName) {
  if (thrownPyExcName == expectedPyExcName) {
    throw HybridException<Exception>{thrownPyExc};
  }
}

/// Name of errors module where exceptions will be registered.
constexpr std::string_view kErrorsModuleName = "openassetio._openassetio.errors";

/**
 * Attempt to convert a given Python exception into one of the C++
 * exceptions in the CppExceptionsAndPyClassNames list (looked up by
 * indices) and throw it.
 *
 * A no-op if no exception matches.
 *
 * @tparam I Indices of exceptions in the CppExceptionsAndPyClassNames
 * list to attempt to convert to.
 * @param thrownPyExc pybind11-wrapped Python exception.
 */
template <std::size_t... I>
void convertPyExceptionAndThrow(const pybind11::error_already_set &thrownPyExc,
                                [[maybe_unused]] std::index_sequence<I...> unused) {
  // We need values from the Python exception object, so must hold the
  // GIL. pybind11::error_already_set::what() does this itself, but we need
  // additional attributes too. Note that acquiring the GIL can cause
  // crashes if the Python interpreter is finalizing (i.e. has been
  // destroyed).
  const pybind11::gil_scoped_acquire gil{};
  // Check module name of Python exception.
  if (thrownPyExc.type().attr("__module__").cast<std::string_view>() != kErrorsModuleName) {
    // Just in case another exception is defined by managers/hosts with
    // the same name in a different namespace.
    return;
  }

  // Extract class name of Python exception.
  const std::string thrownPyExcName{pybind11::str{thrownPyExc.type().attr("__name__")}};

  (throwHybridExceptionIfMatches<CppExceptionsAndPyClassNames::Exceptions<I>>(
       CppExceptionsAndPyClassNames::kClassNames[I], thrownPyExc, thrownPyExcName),
   ...);
}

/**
 * Attempt to convert a given Python exception into a C++ exception
 * in the CppExceptionsAndPyClassNames list, and throw it.
 *
 * A no-op if no exception matches.
 *
 * @param thrownPyExc pybind11-wrapped Python exception.
 */
inline void convertPyExceptionAndThrow(const pybind11::error_already_set &thrownPyExc) {
  convertPyExceptionAndThrow(thrownPyExc, CppExceptionsAndPyClassNames::kIndices);
}

/**
 * Decorate a callable with a try-catch that will catch a
 * pybind11-wrapped Python exception and attempt to convert it to a C++
 * exception before re-throwing.
 *
 * @tparam Fn Type of callable to decorate.
 * @param func Callable instance to decorate.
 * @return Return value of callable, if no exception occurs.
 */
template <class Fn>
auto decorateWithExceptionConverter(Fn &&func) {
  try {
    return func();
  } catch (const pybind11::error_already_set &exc) {
    convertPyExceptionAndThrow(exc);
    // Can't convert exception, so rethrow as-is.
    throw;
  }
}
/**
 * @}
 */
