// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <cstddef>
#include <utility>

#include <openassetio/errors/exceptions.hpp>

#include "./exceptionsConverter.hpp"

namespace {
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
 */
static_assert(assertClassesAreInHierarchyOrder(CppExceptionsAndPyClassNames::kIndices));

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
 * Execute compile-time assertions that all exceptions in the
 * AllExceptions list are also found in the CppExceptionsAndPyClassNames
 * list.
 */
static_assert(
    assertAllExceptionsAreInList(std::make_index_sequence<std::tuple_size_v<AllExceptions>>{}));

/**
 * @}
 */
}  // namespace
