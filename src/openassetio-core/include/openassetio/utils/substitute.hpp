// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#pragma once
#include <string_view>

#include <openassetio/export.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {
/**
 * Substitute placeholders in a given string using the provided
 * dictionary mapping of tokens to values.
 *
 * The input string can contain placeholders in the form of `{key}`
 * where `key` is a key in the provided dictionary. The placeholder will
 * be replaced by the corresponding value from the dictionary.
 *
 * All placeholders must be valid keys in the dictionary. If a
 * placeholder is not found in the dictionary, an exception will be
 * thrown.
 *
 * Integers can be zero-padded in the format string. For example,
 * `{key:03d}` will replace the placeholder with the integer value of
 * `key` from the dictionary, padded with zeros to a width of 3 digits.
 * The format specifier follows `libfmt` / Python format string syntax.
 *
 * Note that no format specifiers other than zero-padding are officially
 * supported, though other specifiers may work. This is to keep the
 * interop surface area as small as possible, e.g. to ease
 * cross-language support.
 *
 * @param input The string in which substitutions are to be made.
 *
 * @param substitutions The dictionary containing the keys to be
 * replaced and their corresponding values.
 *
 * @return The input string with all valid substitutions made.
 *
 * @throws errors.InputValidationException if a substitution variable is
 * not found in the dictionary.
 */
OPENASSETIO_CORE_EXPORT openassetio::Str substitute(
    std::string_view input, const openassetio::InfoDictionary& substitutions);
}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
