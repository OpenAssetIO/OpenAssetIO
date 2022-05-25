// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>  // For OPENASSETIO_CORE_ABI_VERSION

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Provides utilities for converting between C++ types and C handles.
 */
namespace handles {
/**
 * Convert between C++ types and C opaque handles for those types.
 *
 * @tparam Type C++ type.
 * @tparam Handle Opaque handle type.
 */
template <class Type, class Handle>
struct Converter {
  /**
   * Convert a pointer to a C++ instance to a handle.
   *
   * @param ptr Pointer to C++ instance.
   * @return Opaque C handle.
   */
  static Handle toHandle(Type* ptr) { return reinterpret_cast<Handle>(ptr); }

  /**
   * Convert a handle back to the underlying C++ instance.
   *
   * @param handle Handle to unpack.
   * @return Pointer to C++ instance.
   */
  static Type* toInstance(Handle handle) { return reinterpret_cast<Type*>(handle); }
};
}  // namespace handles
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
