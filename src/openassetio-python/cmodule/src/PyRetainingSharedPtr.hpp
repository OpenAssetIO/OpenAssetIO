// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
/**
 * Defines PyRetainingSharedPtr, a custom `shared_ptr` that keeps the Python
 * instance alive whilst the associated C++ instance is alive.
 *
 * This works around https://github.com/pybind/pybind11/issues/1333
 *
 * The solution was inspired by
 * https://github.com/pybind/pybind11/issues/1546
 */
#pragma once

#include <functional>
#include <memory>
#include <type_traits>
#include <utility>

#include <pybind11/pybind11.h>

#include <openassetio/export.h>
// Private headers
#include <openassetio/private/python/pointers.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Custom shared_ptr type for flagging function arguments and trampoline
 * return values that should keep the Python object alive at least as
 * long as the shared_ptr (and any other shared_ptrs copy-constructed
 * from it) is alive.
 *
 * This smart pointer type should be used as the parameter type for
 * functions that take a Python object that inherits from a C++ class
 * and whose Python instance must be kept alive whilst there is still
 * a C++ reference to it.
 *
 * Similarly, this should be used as the return type in any pybind
 * "trampoline" override (i.e. PYBIND_OVERRIDE et al) that returns a
 * base class pointer where the derived class is implemented in Python.
 *
 * Without this we risk "RuntimeError: Tried to call pure virtual
 * function", or similar, if the Python object goes out of scope but a
 * C++ object still holds a shared_ptr to (the C++ base class of) it.
 *
 * @tparam T Wrapped type.
 */
template <class T>
struct PyRetainingSharedPtr : std::shared_ptr<T> {
  using std::shared_ptr<T>::shared_ptr;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

namespace pybind11::detail {
using openassetio::PyRetainingSharedPtr;

/**
 * Custom type caster for PyRetainingSharedPtr.
 *
 * Any function taking a PyRetainingSharedPtr will attempt to use this
 * caster.
 *
 * I.e. this type caster is used for values going into `.def`ed
 * functions, it is matched against the function parameter when
 * attempting to convert a Python object to a C++ object. It is also
 * used when being returned from a C++ function to Python.
 *
 * In short, this works by decoupling the originating shared_ptr holder
 * of the C++ object and the new shared_ptr passed to C++ functions,
 * using the Python refcount to link the two.
 *
 * There are three members of this type caster class to be aware of:
 * - The base class's `value` is a T*.
 * - Our class's `value` (hiding the base class's) is a
 *   PyRetainingSharedPtr<T> (declaration is hidden under the
 *   PYBIND11_TYPE_CASTER macro).
 * - The base class's `holder`, which is a std::shared_ptr<T>. This
 *   is ignored for our purposes, but must be convertible to the holder
 *   type of the originating Python C++ binding.
 *
 * In `load` we use the default base class implementation to retrieve a
 * pointer to the C++ instance into the base class's `value` (and
 * `holder`).
 *
 * We then create a shared_ptr around the corresponding py::object. The
 * act of copy-constructing the py::object into the shared_ptr
 * increments the PyObject refcount.
 *
 * Pybind has a holder (shared_ptr) of its own stored on the PyObject
 * (see pybind11::detail::instance::simple_value_holder et al), which
 * will be destroyed when the PyObject refcount reaches zero. So
 * incrementing the PyObject refcount keeps alive both the PyObject
 * and the originating C++ shared_ptr.
 *
 * Our `value`, which will be passed to the C++ function, is then a
 * PyRetainingSharedPtr<T> that points to the C++ object, but which will
 * decrement the PyObject refcount when destroyed.
 *
 * Decrementing the PyObject refcount may lead to the PyObject being
 * destroyed, and so the originating shared_ptr being destroyed.
 *
 * @tparam T
 */
template <typename T>
class type_caster<PyRetainingSharedPtr<T>> : public type_caster_holder<T, std::shared_ptr<T>> {
  // NOLINTNEXTLINE
  PYBIND11_TYPE_CASTER(PyRetainingSharedPtr<T>, handle_type_name<T>::name);

  using BaseCaster = type_caster_holder<T, std::shared_ptr<T>>;

  bool load(pybind11::handle src, bool convert) {
    // Load into base class data structures, giving us the `value` raw
    // pointer (and the `holder` shared_ptr).
    if (!BaseCaster::load(src, convert)) {
      return false;
    }

    // The refcount will be decremented when this py::object goes out of
    // scope, so we must `borrow` (rather than `steal`) so the refcount
    // is increased first, resulting in net-zero refcount changes due to
    // this line.
    auto pyObj = reinterpret_borrow<object>(src);

    // This is the value that is passed to the C++ function.
    value = openassetio::python::pointers::createPyRetainingPtr<PyRetainingSharedPtr<T>>(
        pyObj, static_cast<T*>(BaseCaster::value));
    return true;
  }
};
}  // namespace pybind11::detail

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Optional helper to decorate a function for use by pybind such that
 * Python objects provided as `shared_ptr`-to-base are not destroyed
 * prematurely.
 *
 * For example, the following snippet will return a new
 * pybind-compatible function (lambda) that wraps `MyClass::myMethod`.
 * This new function will have the same signature as `myMethod`, except
 * that all `shared_ptr<MyType1>` or `shared_ptr<MyType2>` arguments
 * will instead be `PyRetainingSharedPtr<MyType1>` or
 * `PyRetainingSharedPtr<MyType2>`, respectively.
 *
 * @code{.cpp}
 * RetainPyArgs<
 *   shared_ptr<MyType1>,
 *   shared_ptr<MyType2>>::forFn(&MyClass::myMethod)
 * @endcode
 *
 * Also see `contributing/CODING_STANDARDS.md` in the repository.
 *
 * @tparam PtrsToPyRetain `shared_ptr` types whose associated Python
 * instance(s) should be kept alive.
 */
template <class... PtrsToPyRetain>
struct RetainPyArgs {
  /**
   * Return a decorated function that converts given `shared_ptr`
   * argument types to `PyRetainingSharedPtr` types, so that the
   * associated Python instances are not destroyed.
   *
   * @tparam Fn Function to decorate. Can be a free/static function or
   * member function.
   * @return Decorated function suitable for use in a Pybind `.def(...`
   * call.
   */
  template <auto Fn>
  static auto forFn() {
    return decorator<Fn>(Fn);
  }

  template <class Ret, class... Args>
  static auto forFn(std::function<Ret(Args...)> func) {
    return py::cpp_function(
        [func = std::move(func)](ConvertToPyRetainingSharedPtrT<Args>... args) {
          return func(std::forward<ConvertToPyRetainingSharedPtrT<Args>>(args)...);
        });
  }

 private:
  /// Decorate a raw function pointer (i.e. free or static function).
  template <auto Fn, class Ret, class... Args>
  static constexpr auto decorator([[maybe_unused]] Ret (*unused)(Args...)) {
    return [](ConvertToPyRetainingSharedPtrT<Args>... args) {
      return Fn(std::forward<ConvertToPyRetainingSharedPtrT<Args>>(args)...);
    };
  }

  /// Decorate a const member function.
  template <auto Fn, class Ret, class Class, class... Args>
  static constexpr auto decorator([[maybe_unused]] Ret (Class::*unused)(Args...) const) {
    return [](Class& self, ConvertToPyRetainingSharedPtrT<Args>... args) {
      return std::mem_fn(Fn)(self, std::forward<ConvertToPyRetainingSharedPtrT<Args>>(args)...);
    };
  }

  /// Decorate a non-const member function.
  template <auto Fn, class Ret, class Class, class... Args>
  static constexpr auto decorator([[maybe_unused]] Ret (Class::*unused)(Args...)) {
    return [](Class& self, ConvertToPyRetainingSharedPtrT<Args>... args) {
      return std::mem_fn(Fn)(self, std::forward<ConvertToPyRetainingSharedPtrT<Args>>(args)...);
    };
  }

  /**
   * Resolve `Type` to `PyRetainingSharedPtr` if `Class` is a
   * `shared_ptr`.
   *
   * Default case: `Class` is not a `shared_ptr`.
   */
  template <class Class>
  struct PyRetainingIfSharedPtr {
    using Type = std::nullptr_t;
  };

  /**
   * Resolve `Type` to `PyRetainingSharedPtr` if `Class` is a
   * `shared_ptr`.
   *
   * Specialisation: `Class` is a `shared_ptr`.
   */
  template <class T>
  struct PyRetainingIfSharedPtr<std::shared_ptr<T>> {
    using Type = PyRetainingSharedPtr<T>&&;
  };

  /**
   * Search through the list of `PtrsToPyRetain`, attempt to match `Arg`
   * against it, and if successful convert to a `PyRetainingSharedPtr`.
   *
   * `Type` stores the result. Passes through `Arg` unchanged if not
   * found in the list. Otherwise converts to a `PyRetainingSharedPtr`.
   */
  template <class Arg>
  struct ConvertToPyRetainingSharedPtr {
    /**
     * Remove const ref etc from Arg.
     *
     * We assume PtrsToPyRetain is a list of plain `shared_ptr`s, i.e.
     * not const-qualified or reference types. So remove such qualifiers
     * from Arg for comparison purposes.
     */
    using DecayedArg = std::decay_t<Arg>;
    /**
     * Compare a single element of the `PtrsToPyRetain` list against
     * `Arg`.
     */
    template <class PtrToPyRetain>
    struct ConvertIfMatches : std::is_same<DecayedArg, PtrToPyRetain> {
      // Note: this will be `std::nullptr_t` if `PtrToRetain` is not a
      // `shared_ptr`. See `static_assert` below.
      using Type = typename PyRetainingIfSharedPtr<DecayedArg>::Type;
    };

    struct PassThrough : std::true_type {
      using Type = Arg;
    };

    /**
     * Perform the type search.
     *
     * `std::disjunction` is a logical "or" that short-circuits at the
     * first type whose `::value` is true.
     */
    using Type = typename std::disjunction<ConvertIfMatches<PtrsToPyRetain>..., PassThrough>::Type;

    static_assert(!std::is_same_v<Type, std::nullptr_t>,
                  "RetainPyArgs given a type that is not a shared_ptr");
  };

  /// Convenience alias.
  template <class Arg>
  using ConvertToPyRetainingSharedPtrT = typename ConvertToPyRetainingSharedPtr<Arg>::Type;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
