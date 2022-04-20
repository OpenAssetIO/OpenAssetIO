// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

#include "StringView.hpp"
#include "errors.hpp"
#include "handles.hpp"

namespace {

using openassetio::InfoDictionary;
namespace errors = openassetio::errors;
using HandleConverter =
    openassetio::handles::Converter<InfoDictionary, OPENASSETIO_NS(InfoDictionary_h)>;

// Helper for static_assert.
template <class... T>
[[maybe_unused]] constexpr bool kAlwaysFalse = false;

/**
 * Wrap a callable such that some common exceptions are caught and
 * converted to an error code.
 *
 * @tparam Fn Type of callable to wrap.
 * @param err Storage for error message, if any.
 * @param fn Callable to wrap.
 * @return Error code.
 */
template <typename Fn>
OPENASSETIO_NS(ErrorCode)
catchCommonExceptionAsCode(OPENASSETIO_NS(StringView) * err, Fn &&fn) {
  // TODO(DF): @exception messages.
  return errors::catchUnknownExceptionAsCode(err, [&] {
    try {
      return fn();
    } catch (const std::out_of_range &exc) {
      // Default exception message:
      // VS 2019: "invalid unordered_map<K, T> key"
      // GCC 9: "_Map_base::at"
      openassetio::assignStringView(err, "Invalid key");
      return OPENASSETIO_NS(ErrorCode_kOutOfRange);
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
OPENASSETIO_NS(ErrorCode)
get(OPENASSETIO_NS(StringView) * err, Type *out, OPENASSETIO_NS(InfoDictionary_h) handle,
    const OPENASSETIO_NS(ConstStringView) key) {
  const InfoDictionary *infoDictionary = HandleConverter::toInstance(handle);

  return catchCommonExceptionAsCode(err, [&] {
    // TODO(DF): @exception messages.
    try {
      *out = std::get<Type>(infoDictionary->at({key.data, key.size}));
    } catch (const std::bad_variant_access &exc) {
      // Default exception message:
      // VS 2019: "bad variant access"
      // GCC 9: "Unexpected index"
      openassetio::assignStringView(err, "Invalid value type");
      return OPENASSETIO_NS(ErrorCode_kBadVariantAccess);
    }

    return OPENASSETIO_NS(ErrorCode_kOK);
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
void set(OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key,
         Type value) {
  InfoDictionary *infoDictionary = HandleConverter::toInstance(handle);
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
OPENASSETIO_NS(ErrorCode)
set(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) handle,
    const OPENASSETIO_NS(ConstStringView) key, Type value) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    set(handle, key, std::forward<Type>(value));
    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}
}  // namespace

extern "C" {

OPENASSETIO_NS(InfoDictionary_s) OPENASSETIO_NS(InfoDictionary_suite)() {
  return {
      // ctor
      [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) * out) {
        return errors::catchUnknownExceptionAsCode(err, [&] {
          *out = HandleConverter::toHandle(new InfoDictionary{});
          return OPENASSETIO_NS(ErrorCode_kOK);
        });
      },

      // dtor
      [](OPENASSETIO_NS(InfoDictionary_h) handle) { delete HandleConverter::toInstance(handle); },

      // typeOf
      [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_ValueType) * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        return catchCommonExceptionAsCode(err, [&] {
          const InfoDictionary *infoDictionary = HandleConverter::toInstance(handle);

          std::visit(
              [&out](auto &&value) {
                using ValueType = std::decay_t<decltype(value)>;
                if constexpr (std::is_same_v<ValueType, openassetio::Bool>) {
                  *out = OPENASSETIO_NS(InfoDictionary_ValueType_kBool);
                } else if constexpr (std::is_same_v<ValueType, openassetio::Int>) {
                  *out = OPENASSETIO_NS(InfoDictionary_ValueType_kInt);
                } else if constexpr (std::is_same_v<ValueType, openassetio::Float>) {
                  *out = OPENASSETIO_NS(InfoDictionary_ValueType_kFloat);
                } else if constexpr (std::is_same_v<ValueType, openassetio::Str>) {
                  *out = OPENASSETIO_NS(InfoDictionary_ValueType_kStr);
                } else {
                  static_assert(kAlwaysFalse<ValueType>, "Unhandled variant type");
                }
              },
              infoDictionary->at({key.data, key.size}));

          return OPENASSETIO_NS(ErrorCode_kOK);
        });
      },

      // Through the magic of template type deduction...
      // getBool
      &get,
      // getInt
      &get,
      // getFloat
      &get,

      // getStr
      [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        openassetio::Str str;
        const OPENASSETIO_NS(ErrorCode) errorCode = get(err, &str, handle, key);

        if (errorCode != OPENASSETIO_NS(ErrorCode_kOK)) {
          return errorCode;
        }

        openassetio::assignStringView(out, str);

        if (str.size() > out->capacity) {
          openassetio::assignStringView(err, "Insufficient storage for return value");
          return OPENASSETIO_NS(ErrorCode_kLengthError);
        }

        return OPENASSETIO_NS(ErrorCode_kOK);
      },

      // Through the magic of template type deduction...
      // setBool
      &set,
      // setInt
      &set,
      // setFloat
      &set,

      // setStr
      [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) handle,
         const OPENASSETIO_NS(ConstStringView) key, const OPENASSETIO_NS(ConstStringView) value) {
        return errors::catchUnknownExceptionAsCode(err, [&] {
          set(handle, key, openassetio::Str{value.data, value.size});
          return OPENASSETIO_NS(ErrorCode_kOK);
        });
      }};
}
}  // extern "C"
