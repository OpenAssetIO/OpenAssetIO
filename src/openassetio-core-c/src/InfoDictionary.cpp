// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <cstddef>
#include <stdexcept>
#include <type_traits>
#include <variant>

#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

#include "StringView.hpp"
#include "errors.hpp"
#include "handles/InfoDictionary.hpp"

using openassetio::InfoDictionary;
namespace errors = openassetio::errors;
namespace handles = openassetio::handles;

namespace {
// Helper for static_assert.
template <class... T>
[[maybe_unused]] constexpr bool kAlwaysFalse = false;

/**
 * Wrap a callable such that some common exceptions are caught and
 * converted to an error code.
 *
 * @tparam Fn Type of callable to wrap.
 * @param err Storage for error message, if any.
 * @param callable Callable to wrap.
 * @return Error code.
 */
template <typename Fn>
oa_ErrorCode catchCommonExceptionAsCode(oa_StringView *err, const Fn &callable) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    try {
      return callable();
    } catch ([[maybe_unused]] const std::out_of_range &exc) {
      // Default exception message:
      // VS 2019: "invalid unordered_map<K, T> key"
      // GCC 9: "_Map_base::at"
      openassetio::assignStringView(err, "Invalid key");
      return oa_ErrorCode_kOutOfRange;
    }
  });
}

/**
 * Get a primitive value from a InfoDictionary, converting exceptions to
 * error codes.
 *
 * @tparam Type Type of value to extract from variant.
 * @param[out] err Storage for error message, if any.
 * @param[out] out Storage for return value.
 * @param handle Opaque handle to a InfoDictionary.
 * @param key Key to query within InfoDictionary.
 * @return Error code.
 */
template <class Type>
oa_ErrorCode get(oa_StringView *err, Type *out, oa_InfoDictionary_h handle,
                 const oa_ConstStringView key) {
  const InfoDictionary *infoDictionary = handles::InfoDictionary::toInstance(handle);

  return catchCommonExceptionAsCode(err, [&] {
    try {
      *out = std::get<Type>(infoDictionary->at({key.data, key.size}));
    } catch ([[maybe_unused]] const std::bad_variant_access &exc) {
      // Default exception message:
      // VS 2019: "bad variant access"
      // GCC 9: "Unexpected index"
      openassetio::assignStringView(err, "Invalid value type");
      return oa_ErrorCode_kBadVariantAccess;
    }

    return oa_ErrorCode_kOK;
  });
}

/**
 * Set a value in a InfoDictionary via C handle.
 *
 * @tparam Type Type of value to set in variant.
 * @param handle Opaque handle to a InfoDictionary.
 * @param key Key to set within InfoDictionary.
 * @param value Value to set within InfoDictionary.
 */
template <class Type>
void set(oa_InfoDictionary_h handle, const oa_ConstStringView key, Type value) {
  InfoDictionary *infoDictionary = handles::InfoDictionary::toInstance(handle);
  infoDictionary->insert_or_assign(openassetio::Str{key.data, key.size},
                                   std::forward<Type>(value));
}

/**
 * Set a value in a InfoDictionary, converting exceptions to error codes.
 *
 * @tparam Type Type of value to set in variant.
 * @param[out] err Storage for error message, if any.
 * @param handle Opaque handle to a InfoDictionary.
 * @param key Key to set within InfoDictionary.
 * @param value Value to set within InfoDictionary.
 * @return Error code.
 */
template <class Type>
oa_ErrorCode set(oa_StringView *err, oa_InfoDictionary_h handle, const oa_ConstStringView key,
                 Type value) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    set(handle, key, std::forward<Type>(value));
    return oa_ErrorCode_kOK;
  });
}
}  // namespace

extern "C" {

oa_ErrorCode oa_InfoDictionary_ctor(oa_StringView *error, oa_InfoDictionary_h *out) {
  return errors::catchUnknownExceptionAsCode(error, [&] {
    *out = handles::InfoDictionary::toHandle(new InfoDictionary{});
    return oa_ErrorCode_kOK;
  });
}

void oa_InfoDictionary_dtor(oa_InfoDictionary_h handle) {
  delete handles::InfoDictionary::toInstance(handle);
}

std::size_t oa_InfoDictionary_size(oa_InfoDictionary_h handle) {
  return handles::InfoDictionary::toInstance(handle)->size();
}

oa_ErrorCode oa_InfoDictionary_typeOf(oa_StringView *error, oa_InfoDictionary_ValueType *out,
                                      oa_InfoDictionary_h handle, const oa_ConstStringView key) {
  return catchCommonExceptionAsCode(error, [&] {
    const InfoDictionary *infoDictionary = handles::InfoDictionary::toInstance(handle);

    std::visit(
        [&out]([[maybe_unused]] auto &&value) {
          using ValueType = std::decay_t<decltype(value)>;
          if constexpr (std::is_same_v<ValueType, openassetio::Bool>) {
            *out = oa_InfoDictionary_ValueType_kBool;
          } else if constexpr (std::is_same_v<ValueType, openassetio::Int>) {
            *out = oa_InfoDictionary_ValueType_kInt;
          } else if constexpr (std::is_same_v<ValueType, openassetio::Float>) {
            *out = oa_InfoDictionary_ValueType_kFloat;
          } else if constexpr (std::is_same_v<ValueType, openassetio::Str>) {
            *out = oa_InfoDictionary_ValueType_kStr;
          } else {
            static_assert(kAlwaysFalse<ValueType>, "Unhandled variant type");
          }
        },
        infoDictionary->at({key.data, key.size}));

    return oa_ErrorCode_kOK;
  });
}

oa_ErrorCode oa_InfoDictionary_getBool(oa_StringView *error, openassetio::Bool *out,
                                       oa_InfoDictionary_h handle, const oa_ConstStringView key) {
  return get<openassetio::Bool>(error, out, handle, key);
}

oa_ErrorCode oa_InfoDictionary_getInt(oa_StringView *error, openassetio::Int *out,
                                      oa_InfoDictionary_h handle, const oa_ConstStringView key) {
  return get<openassetio::Int>(error, out, handle, key);
}

oa_ErrorCode oa_InfoDictionary_getFloat(oa_StringView *error, openassetio::Float *out,
                                        oa_InfoDictionary_h handle, const oa_ConstStringView key) {
  return get<openassetio::Float>(error, out, handle, key);
}

oa_ErrorCode oa_InfoDictionary_getStr(oa_StringView *error, oa_StringView *out,
                                      oa_InfoDictionary_h handle, const oa_ConstStringView key) {
  openassetio::Str str;

  if (const oa_ErrorCode errorCode = get(error, &str, handle, key);
      errorCode != oa_ErrorCode_kOK) {
    return errorCode;
  }

  openassetio::assignStringView(out, str);

  if (str.size() > out->capacity) {
    openassetio::assignStringView(error, "Insufficient storage for return value");
    return oa_ErrorCode_kLengthError;
  }

  return oa_ErrorCode_kOK;
}

oa_ErrorCode oa_InfoDictionary_setBool(oa_StringView *error, oa_InfoDictionary_h handle,
                                       const oa_ConstStringView key,
                                       const openassetio::Bool value) {
  return set<openassetio::Bool>(error, handle, key, value);
}

oa_ErrorCode oa_InfoDictionary_setInt(oa_StringView *error, oa_InfoDictionary_h handle,
                                      const oa_ConstStringView key, const openassetio::Int value) {
  return set<openassetio::Int>(error, handle, key, value);
}

oa_ErrorCode oa_InfoDictionary_setFloat(oa_StringView *error, oa_InfoDictionary_h handle,
                                        const oa_ConstStringView key,
                                        const openassetio::Float value) {
  return set<openassetio::Float>(error, handle, key, value);
}

oa_ErrorCode oa_InfoDictionary_setStr(oa_StringView *error, oa_InfoDictionary_h handle,
                                      const oa_ConstStringView key,
                                      const oa_ConstStringView value) {
  return errors::catchUnknownExceptionAsCode(error, [&] {
    set(handle, key, openassetio::Str{value.data, value.size});
    return oa_ErrorCode_kOK;
  });
}
}  // extern "C"
