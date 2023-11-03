// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <map>
#include <string_view>
#include <tuple>
#include <type_traits>

#include <pybind11/eval.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/errors/exceptions.hpp>

#include "../_openassetio.hpp"

namespace {
using openassetio::errors::BatchElementException;
using openassetio::errors::ConfigurationException;
using openassetio::errors::InputValidationException;
using openassetio::errors::NotImplementedException;
using openassetio::errors::OpenAssetIOException;
using openassetio::errors::UnhandledException;

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
constexpr auto kCppExceptionsAndPyClassNames =
    TypesAndIds<BatchElementException, NotImplementedException, UnhandledException,
                ConfigurationException, InputValidationException, OpenAssetIOException>{
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
 * @section asserts Compile-time assertions.
 *
 * Ensure exception list is in the correct order and is exhaustive.
 *
 * @{
 */

/**
 * Utility structure to help assert that the list of C++ exception
 * classes in CppExceptionsAndPyClassNames is in the correct order (i.e.
 * base classes at the end).
 *
 * @tparam I Index of the exception class under test.
 */
template <std::size_t I>
struct AssertClassHierarchyForClassAtIndex {
  /**
   * Assert that none of the given classes (looked up by index) are
   * a base class of the class under test.
   *
   * @tparam J Indices of classes to assert are not a base of the class
   * under test.
   */
  template <std::size_t... J>
  static constexpr void assertNoneOfGivenClassIndicesIsABase(
      [[maybe_unused]] std::index_sequence<J...> unused) {
    (assertClassAtIndexIsNotABase<J>(), ...);
  }

  /**
   * Assert that a particular class (looked up by index) is not a base
   * class of the class under test.
   *
   * @tparam J Index of class to assert is not a base of the class under
   * test.
   */
  template <std::size_t J>
  static constexpr void assertClassAtIndexIsNotABase() {
    static_assert(!std::is_base_of_v<CppExceptionsAndPyClassNames::Exceptions<J>,
                                     CppExceptionsAndPyClassNames::Exceptions<I>>,
                  "Base classes must come after subclasses in kCppExceptionsAndPyClassNames");
  }

  /**
   * Convenience for a compile-time collection of indices in the list
   * that come before the class under test.
   */
  static constexpr auto kPreviousIndices = std::make_index_sequence<I>{};
};

/**
 * Assert that a set of classes (looked up by index) in the
 * CppExceptionsAndPyClassNames list does not have any base classes
 * appearing before them in the list.
 *
 * @tparam I Indices of classes to assert have no base classes at lower
 * indices in the list.
 */
template <std::size_t... I>
constexpr bool assertClassesAreInHierarchyOrder(
    [[maybe_unused]] std::index_sequence<I...> unused) {
  (AssertClassHierarchyForClassAtIndex<I>::assertNoneOfGivenClassIndicesIsABase(
       AssertClassHierarchyForClassAtIndex<I>::kPreviousIndices),
   ...);
  return true;
}
/**
 * Execute compile-time assertions that no class in the
 * CppExceptionsAndPyClassNames list has a base class at a lower index
 * in the list.
 *
 * The resulting value is unused - it's just kludge to make the
 * compiler make the attempt and so fail on any violated static_asserts.
 */
[[maybe_unused]] constexpr bool kIsClassListOrderValid =
    assertClassesAreInHierarchyOrder(CppExceptionsAndPyClassNames::kIndices);

/// List of all OpenAssetIO-specific C++ exceptions.
using openassetio::errors::AllExceptions;

/**
 * Assert that an exception in the AllExceptions list (looked up by
 * index) is found in the given subset of the
 * CppExceptionsAndPyClassNames list (looked up by indices).
 *
 * In practice the subset should be the full set.
 *
 * @tparam I Index of exception in AllExceptions.
 * @tparam J Indices of exceptions in CppExceptionsAndPyClassNames.
 */
template <std::size_t I, std::size_t... J>
constexpr void assertExceptionIsInList([[maybe_unused]] std::index_sequence<J...> unused) {
  static_assert((std::is_same_v<std::tuple_element_t<I, AllExceptions>,
                                CppExceptionsAndPyClassNames::Exceptions<J>> ||
                 ...),
                "Exception is missing from kCppExceptionsAndPyClassNames");
}

/**
 * Assert that a subset of exceptions in the AllExceptions list (looked
 * up by indices) are all found in the CppExceptionsAndPyClassNames
 * list.
 *
 * In practice the subset should be the full set.
 *
 * @tparam I Indices of exceptions in AllExceptions.
 */
template <std::size_t... I>
constexpr bool assertAllExceptionsAreInList([[maybe_unused]] std::index_sequence<I...> unused) {
  (assertExceptionIsInList<I>(CppExceptionsAndPyClassNames::kIndices), ...);
  return true;
}
/**
 * Assert that all exceptions in the AllExceptions list are also found
 * in the CppExceptionsAndPyClassNames list.
 *
 * The resulting value is unused - it's just kludge to make the
 * compiler make the attempt and so fail on any violated static_asserts.
 */
[[maybe_unused]] constexpr bool kIsClassListExhaustive =
    assertAllExceptionsAreInList(std::make_index_sequence<std::tuple_size_v<AllExceptions>>{});

/**
 * @}
 */

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
 * @param pyModule Python module containing Python exception class.
 * @param pyClassName Python exception class name to look up in @p
 * pyModule.
 */
template <class Exception>
void setPyException(const Exception &exception, const py::module_ &pyModule,
                    // TODO(DF): False positive in clang-tidy 12 :(
                    // NOLINTNEXTLINE(readability-avoid-const-params-in-decls)
                    const std::string_view pyClassName) {
  const py::object pyClass = pyModule.attr(pyClassName.data());
  const py::object pyInstance = [&] {
    if constexpr (std::is_same_v<Exception, BatchElementException>) {
      return pyClass(exception.index, exception.error, exception.what());
    } else {
      return pyClass(exception.what());
    }
  }();
  PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());
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
 * @tparam I Index of exception type to catch in
 * CppExceptionsAndPyClassNames list.
 * @param pyModule Python module containing Python exception classes.
 * @param pexc C++ exception to rethrow.
 */
template <std::size_t I>
void tryCatch(const py::module_ &pyModule, std::exception_ptr pexc) {
  try {
    if constexpr (I == 0) {
      std::rethrow_exception(std::move(pexc));
    } else {
      tryCatch<I - 1>(pyModule, std::move(pexc));
    }
  } catch (const CppExceptionsAndPyClassNames::Exceptions<I> &cppExc) {
    setPyException(cppExc, pyModule, CppExceptionsAndPyClassNames::kClassNames[I]);
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
      const py::object pyBaseClass = registeredExceptions.at(kPyBaseClassName);
      // Register the exception, inheriting from looked-up base.
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

/// Name of errors module where exceptions will be registered.
constexpr std::string_view kErrorsModuleName = "openassetio._openassetio.errors";
}  // namespace

/**
 * Register Python exceptions with pybind11.
 *
 * @param mod Python module to hold new Python exception classes.
 */
void registerExceptions(const py::module &mod) {
  // Ensure module name matches what we expect, since it must be
  // imported by name in `register_exception_translator`, below.
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
  // function.
  py::register_exception_translator([](std::exception_ptr pexc) {
    if (!pexc) {
      return;
    }
    const py::module_ pyModule = py::module_::import(kErrorsModuleName.data());

    // Handle the different possible C++ exceptions, creating the
    // corresponding Python exception and setting it as the active
    // exception in this thread.
    tryCatch<CppExceptionsAndPyClassNames::kSize - 1>(pyModule, std::move(pexc));
  });
}

/**
 * @}
 */
