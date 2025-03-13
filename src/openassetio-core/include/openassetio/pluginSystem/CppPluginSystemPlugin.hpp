// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

OPENASSETIO_DECLARE_PTR(CppPluginSystemPlugin)

/**
 * The base class that defines a plugin of the C++ plugin system.
 *
 * @see CppPluginSystemManagerPlugin for a more concrete use case.
 */
// NOLINTNEXTLINE(cppcoreguidelines-special-member-functions)
class OPENASSETIO_CORE_EXPORT CppPluginSystemPlugin {
 public:
  OPENASSETIO_ALIAS_PTR(CppPluginSystemPlugin)
  /// Defaulted virtual destructor.
  virtual ~CppPluginSystemPlugin();

  /**
   * Get the unique identifier of the plugin.
   *
   * The identifier should use only alpha-numeric characters and '.',
   * '_' or '-'. For example:
   *
   *    "org.openassetio.test.manager"
   *
   * @return Plugin's unique identifier.
   */
  [[nodiscard]] virtual openassetio::Identifier identifier() const = 0;
};

/**
 * Function pointer to a factory that produces instances of
 * @ref CppPluginSystemPlugin wrapped in a `shared_ptr`.
 *
 * A pointer to such a function must be returned from an exposed entry
 * point function (with C linkage) from a plugin shared library binary.
 * This function pointer is then called to get the @ref
 * CppPluginSystemPlugin instance.
 *
 * This two-step process is required to work around Windows disallowing
 * C linkage functions from returning C++ types. That is, the entry
 * point with C linkage returns a raw pointer (to a function). The
 * returned PluginFactory function pointer can then point to a C++
 * linkage function, which is allowed to return a
 * CppPluginSystemPluginPtr on Windows.
 *
 * Exception behaviour varies by platform for functions called via
 * pointers retrieved in this way. In particular, the process is
 * terminated with an "access violation" error on Windows. So for
 * cross-platform consistency, the function is marked `noexcept` - it is
 * not valid to throw an exception within a PluginFactory.
 */
using PluginFactory = openassetio::pluginSystem::CppPluginSystemPluginPtr (*)() noexcept;
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
