// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Comparison and stream operators to simplify asserting and reporting
 * of StringView instances during tests.
 *
 * @todo Move these operators out of tests to form part of the public
 * API. We expect such operators to be useful more broadly. This will
 * require some design work, however (e.g. is `capacity` compared when
 * determining StringView equality?).
 */
#pragma once
#include <openassetio/c/StringView.h>
#include <openassetio/c/namespace.h>

#include <openassetio/typedefs.hpp>

/// Comparison operator to allow CHECKing two `StringView`s are equal.
inline bool operator==(const oa_StringView& lhs, const oa_StringView& rhs) {
  return lhs.size == rhs.size && lhs.capacity == rhs.capacity && lhs.data == rhs.data;
}

/// Comparison operator to allow CHECKing if a `StringView` and a
/// string-like container are equal.
template <typename Str>
inline bool operator==(const oa_StringView& lhs, const Str& rhs) {
  return std::string_view{lhs.data, lhs.size} == rhs;
}

/// Comparison operator to allow CHECKing if a `ConstStringView` and a
/// string-like container are equal.
template <typename Str>
inline bool operator==(const oa_ConstStringView& lhs, const Str& rhs) {
  return std::string_view{lhs.data, lhs.size} == rhs;
}

/// Support printing StringView in case assertions fail.
inline std::ostream& operator<<(std::ostream& os, const oa_StringView& rhs) {
  os << "\"" << std::string_view{rhs.data, rhs.size} << "\"";
  return os;
}

/// Support printing ConstStringView in case assertions fail.
inline std::ostream& operator<<(std::ostream& os, const oa_ConstStringView& rhs) {
  os << "\"" << std::string_view{rhs.data, rhs.size} << "\"";
  return os;
}
