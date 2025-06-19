// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once
/**
 * Forward declare a shared_ptr for a given class.
 *
 * Assumes the surrounding namespace is valid for the given class.
 *
 * Declares both non-const and const variants as `ClassPtr` and
 * `ClassConstPtr`, respectively.
 */
#define OPENASSETIO_DECLARE_PTR(Class)             \
  /* NOLINTNEXTLINE(bugprone-macro-parentheses) */ \
  class Class;                                     \
  /* NOLINT(build/include_what_you_use) */         \
  using Class##Ptr = std::shared_ptr<Class>;       \
  using Class##ConstPtr = std::shared_ptr<const Class>;  // NOLINT(build/include_what_you_use)

/**
 * Create unqualified shared_ptr aliases of qualified shared_ptr
 * aliases.
 *
 * Used to define `Ptr`/`ConstPtr` aliases within class definitions,
 * thus allowing their use in generic programming, e.g. `typename
 * T::Ptr`.
 *
 * @note This requires OPENASSETIO_DECLARE_PTR to have been invoked for
 * the target class.
 */
#define OPENASSETIO_ALIAS_PTR(Class) \
  using Ptr = Class##Ptr;            \
  using ConstPtr = Class##ConstPtr;

/**
 * Forward declare a class and its smart pointers.
 *
 * Wraps the declaration in the top-level openassetio and ABI
 * namespaces.
 *
 * If two arguments are given, then the first argument gives a namespace
 * to further wrap the declarations in, and the second argument gives
 * the class name.
 *
 * If only a single argument is provided, then this is assumed to be
 * the class name and is only wrapped in the top-level namespaces.
 */
#define OPENASSETIO_FWD_DECLARE(...) \
  OPENASSETIO_PP_EXPAND(             \
      OPENASSETIO_FWD_DECLARE_(__VA_ARGS__, IN_NS(__VA_ARGS__), TOP_LEVEL_NS(__VA_ARGS__), 0))

/**
 * @private Utility to forward declare a class and its smart pointers.
 *
 * Wraps the declarations in the top-level openassetio and ABI
 * namespaces, then the provided namespace.
 */
#define OPENASSETIO_FWD_DECLARE_IN_NS(Namespace, Class) \
  namespace openassetio {                               \
  inline namespace OPENASSETIO_CORE_ABI_VERSION {       \
  namespace Namespace {                                 \
  OPENASSETIO_DECLARE_PTR(Class)                        \
  }                                                     \
  }                                                     \
  }

/**
 * @private Utility to forward declare a class and its smart pointers.
 *
 * Wraps the declarations in the top-level openassetio and ABI
 * namespaces.
 */
#define OPENASSETIO_FWD_DECLARE_TOP_LEVEL_NS(Class) \
  namespace openassetio {                           \
  inline namespace OPENASSETIO_CORE_ABI_VERSION {   \
  OPENASSETIO_DECLARE_PTR(Class)                    \
  }                                                 \
  }

/**
 * @private Utility to dispatch to the appropriate single-argument or
 * two-argument macro.
 */
#define OPENASSETIO_FWD_DECLARE_(_2, _1, IN_NS_OR_TOP_LEVEL, ...) \
  OPENASSETIO_FWD_DECLARE_##IN_NS_OR_TOP_LEVEL

/**
 * @private Utility to work around MSVC treatment of variadic macros.
 *
 * When `x` is a function-like macro call, the effect is to defer
 * expansion of `x` until the next pass, so that any `__VA_ARGS__` used
 * in the `x` call are substituted on the earlier pass. If we don't use
 * this trick, then MSVC treats the `__VA_ARGS__` as a single argument
 * to the macro, even if it contains multiple arguments.
 *
 * This could also be worked around by using the `/Zc:preprocessor`
 * compiler switch when building with MSVC. However, we would rather
 * avoid mandating specific compiler switches for hosts/plugins when
 * possible.
 */
#define OPENASSETIO_PP_EXPAND(x) x
