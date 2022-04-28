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
using HandleConverter =
    openassetio::handles::Converter<InfoDictionary, OPENASSETIO_NS(InfoDictionary_h)>;

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

  return openassetio::errors::catchUnknownExceptionAsCode(err, [&] {
    // TODO(DF): @exception messages.
    try {
      *out = std::get<Type>(infoDictionary->at({key.data, key.size}));
    } catch (const std::out_of_range &exc) {
      // Default exception message:
      // VS 2019: "invalid unordered_map<K, T> key"
      // GCC 9: "_Map_base::at"
      openassetio::assignStringView(err, "Invalid key");
      return OPENASSETIO_NS(ErrorCode_kOutOfRange);
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
}  // namespace

extern "C" {

OPENASSETIO_NS(InfoDictionary_s) OPENASSETIO_NS(InfoDictionary_suite)() {
  return {
      // dtor
      [](OPENASSETIO_NS(InfoDictionary_h) handle) { delete HandleConverter::toInstance(handle); },
      // getBool
      [](OPENASSETIO_NS(StringView) * err, openassetio::Bool * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        return get<openassetio::Bool>(err, out, handle, key);
      },
      // getInt
      [](OPENASSETIO_NS(StringView) * err, openassetio::Int * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        return get<openassetio::Int>(err, out, handle, key);
      },
      // getFloat
      [](OPENASSETIO_NS(StringView) * err, openassetio::Float * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        return get<openassetio::Float>(err, out, handle, key);
      },
      // getStr
      [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
         OPENASSETIO_NS(InfoDictionary_h) handle, const OPENASSETIO_NS(ConstStringView) key) {
        openassetio::Str str;
        const OPENASSETIO_NS(ErrorCode) errorCode = get<openassetio::Str>(err, &str, handle, key);

        if (errorCode != OPENASSETIO_NS(ErrorCode_kOK)) {
          return errorCode;
        }

        openassetio::assignStringView(out, str);

        if (str.size() > out->capacity) {
          openassetio::assignStringView(err, "Insufficient storage for return value");
          return OPENASSETIO_NS(ErrorCode_kLengthError);
        }

        return OPENASSETIO_NS(ErrorCode_kOK);
      }};
}
}  // extern "C"
