// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#pragma once

#include <pybind11/pybind11.h>

#include "./errors/exceptionsConverter.hpp"

/// @note Update errorsTest.cpp if adding more override macros below.

/**
 * Decorate PYBIND11_OVERRIDE_NAME with exception type translation.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE_NAME(ret_type, cname, name, fn, ...)                      \
  do { /* NOLINT(cppcoreguidelines-avoid-do-while) */                                           \
    /* Must explicitly specify decorated lambda return type, since    */                        \
    /* PYBIND11_OVERRIDE_IMPL return type can be PyRetainingSharedPtr,*/                        \
    /* which confuses the compiler.                                   */                        \
    return decorateWithExceptionConverter([&]() -> decltype(cname::fn(__VA_ARGS__)) {           \
      PYBIND11_OVERRIDE_IMPL(PYBIND11_TYPE(ret_type), PYBIND11_TYPE(cname), name, __VA_ARGS__); \
      return cname::fn(__VA_ARGS__);                                                            \
    });                                                                                         \
  } while (false)

/**
 * Decorate PYBIND11_OVERRIDE with exception type translation.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE(ret_type, cname, fn, ...)                              \
  OPENASSETIO_PYBIND11_OVERRIDE_NAME(PYBIND11_TYPE(ret_type), PYBIND11_TYPE(cname), #fn, fn, \
                                     __VA_ARGS__)

/**
 * Similar to OPENASSETIO_PYBIND11_OVERRIDE, but allows different
 * arguments to be given to the Python implementation and the C++
 * fallback (base class) implementation.
 *
 * For example, this is useful to decorate std::function callbacks
 * with `PyRetainingSharedPtr`s, so that Python objects are kept alive
 * as they pass through C++ callbacks.
 *
 * The CppArgs parameter must be a parentheses-enclosed,
 * comma-separated, list of arguments. These are given to the C++ base
 * class implementation, if no Python override is found.
 *
 * All remaining arguments following the CppArgs (not
 * parentheses-enclosed) are passed to the Python override
 * implementation, if one exists.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE_ARGS(Ret, Class, Fn, CppArgs, ... /* PyArgs */)     \
  do { /* NOLINT(cppcoreguidelines-avoid-do-while) */                                     \
    return decorateWithExceptionConverter([&]() -> decltype(Class::Fn CppArgs) {          \
      PYBIND11_OVERRIDE_IMPL(PYBIND11_TYPE(Ret), PYBIND11_TYPE(Class), #Fn, __VA_ARGS__); \
      return Class::Fn CppArgs;                                                           \
    });                                                                                   \
  } while (false)

/**
 * Work around https://github.com/pybind/pybind11/issues/4878 and
 * decorate PYBIND11_OVERRIDE_PURE_NAME with exception type translation.
 *
 * In a Debug build, where `assert` is enabled, pybind11 will do an
 * `assert(!PyErr_Occurred())` before throwing "Tried to call pure
 * virtual function". Since Python 3.9, the PyErr_Occurred() function
 * requires the GIL to be acquired.
 *
 * The following macro duplicates PYBIND11_OVERRIDE_PURE_NAME and
 * inserts a `gil_scoped_acquire`, in order to work around the problem
 * until it is fixed upstream.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE_PURE_NAME(ret_type, cname, name, fn, ...)                 \
  do { /* NOLINT(cppcoreguidelines-avoid-do-while) */                                           \
    return decorateWithExceptionConverter([&]() -> decltype(cname::fn(__VA_ARGS__)) {           \
      PYBIND11_OVERRIDE_IMPL(PYBIND11_TYPE(ret_type), PYBIND11_TYPE(cname), name, __VA_ARGS__); \
      const pybind11::gil_scoped_acquire gil{};                                                 \
      pybind11::pybind11_fail(                                                                  \
          "Tried to call pure virtual function \"" PYBIND11_STRINGIFY(cname) "::" name "\"");   \
    });                                                                                         \
  } while (false)

/**
 * Work around https://github.com/pybind/pybind11/issues/4878 and
 * decorate PYBIND11_OVERRIDE_PURE with exception type translation.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE_PURE(ret_type, cname, fn, ...)                              \
  OPENASSETIO_PYBIND11_OVERRIDE_PURE_NAME(PYBIND11_TYPE(ret_type), PYBIND11_TYPE(cname), #fn, fn, \
                                          __VA_ARGS__)
