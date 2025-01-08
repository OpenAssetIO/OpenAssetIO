// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include "Regex.hpp"

#include <cassert>
#include <cstddef>
#include <optional>
#include <string_view>
#include <type_traits>

#include <fmt/core.h>
#include <pcre2.h>

#include <openassetio/export.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {

namespace {
constexpr Str::size_type kErrorMessageMaxLength = 1000;

Str errorCodeToMessage(const int errorCode) {
  Str errorMessage(kErrorMessageMaxLength, '\0');

  static_assert(sizeof(Str::value_type) == sizeof(PCRE2_UCHAR8), "PCRE2 char type size mismatch");

  const auto errorMessageLength = pcre2_get_error_message(
      // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
      errorCode, reinterpret_cast<PCRE2_UCHAR8*>(errorMessage.data()), errorMessage.size());
  errorMessage.resize(static_cast<Str::size_type>(errorMessageLength));
  return errorMessage;
}
}  // namespace

Regex::Regex(const std::string_view pattern) {
  int errorCode = 0;
  std::size_t errorOffset = 0;

  static_assert(sizeof(std::string_view::value_type) == sizeof(std::remove_pointer_t<PCRE2_SPTR8>),
                "PCRE2 char type size mismatch");

  code_ = pcre2_compile(
      // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
      reinterpret_cast<PCRE2_SPTR8>(pattern.data()), pattern.size(),
      PCRE2_CASELESS | PCRE2_DOLLAR_ENDONLY |
          PCRE2_DOTALL, /* case-insensitive; `$` matches end of string; `.` matches newlines */
      &errorCode,       /* error number */
      &errorOffset,     /* error offset */
      nullptr);         /* use default compile context */

  if (code_ == nullptr) {
    throw errors::InputValidationException{fmt::format(
        "Error {} compiling regex '{}': {}", errorCode, pattern, errorCodeToMessage(errorCode))};
  }

  // Extra performance JIT compile. We don't care about partial
  // matches.
  errorCode = pcre2_jit_compile(code_, PCRE2_JIT_COMPLETE);

  if (errorCode != 0) {
    throw errors::InputValidationException{fmt::format(
        "Error {} JIT compiling '{}': {}", errorCode, pattern, errorCodeToMessage(errorCode))};
  }
}

Regex::~Regex() { pcre2_code_free(code_); }

std::optional<Regex::Match> Regex::match(const std::string_view subject) const {
  Match matchObj{code_};

  static_assert(sizeof(std::string_view::value_type) == sizeof(std::remove_pointer_t<PCRE2_SPTR8>),
                "PCRE2 char type size mismatch");

  const int numMatches =
      pcre2_jit_match(code_, /* regex object */
                             // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
                      reinterpret_cast<PCRE2_SPTR8>(subject.data()), /* subject */
                      subject.size(),                                /* length of subject */
                      0,                     /* start at offset 0 in the subject */
                      0,                     /* default options */
                      matchObj.data().get(), /* block for storing the result */
                      nullptr);              /* use default match context */

  if (numMatches < 0 && numMatches != PCRE2_ERROR_NOMATCH) {
    throw errors::InputValidationException{fmt::format("Error {} matching regex to '{}': {}",
                                                       numMatches, subject,
                                                       errorCodeToMessage(numMatches))};
  }

  if (numMatches > 0) {
    return matchObj;
  }

  return std::nullopt;
}

Str Regex::substituteToReduceSize(const std::string_view& subject,
                                  const std::string_view& replacement) const {
  if (subject.empty()) {
    // Zero-size buffer is immediately an error in pcre, so just short-circuit.
    return {};
  }
  // `+ 1` so pcre knows it has enough space for a null terminator.
  Str result(subject.size() + 1, '\0');
  std::size_t resultSize = result.size();

  static_assert(sizeof(std::string_view::value_type) == sizeof(std::remove_pointer_t<PCRE2_SPTR8>),
                "PCRE2 char type size mismatch");
  static_assert(sizeof(Str::value_type) == sizeof(PCRE2_UCHAR8), "PCRE2 char type size mismatch");

  const int numSubstitutions =
      pcre2_substitute(code_, /* regex object */
                              // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
                       reinterpret_cast<PCRE2_SPTR8>(subject.data()), /* subject */
                       subject.size(),                                /* length of subject */
                       0,                         /* start at offset 0 in the subject */
                       PCRE2_SUBSTITUTE_GLOBAL,   /* substitute all matches */
                       Match{code_}.data().get(), /* block for storing the result */
                       nullptr,                   /* use default match context */
                       // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
                       reinterpret_cast<PCRE2_SPTR8>(replacement.data()), /* replacement */
                       replacement.size(),                                /* replacement length */
                       // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
                       reinterpret_cast<PCRE2_UCHAR8*>(result.data()), /* output buffer */
                       &resultSize                                     /* output buffer size */
      );

  if (numSubstitutions < 0) {
    throw errors::InputValidationException{
        fmt::format("Error {} substituting regex matches in '{}' with '{}': {}", numSubstitutions,
                    subject, replacement, errorCodeToMessage(numSubstitutions))};
  }

  result.resize(resultSize);
  return result;
}

Regex::Match::Match(const pcre2_code_8* code)
    : data_{pcre2_match_data_create_from_pattern(code, nullptr)} {
  if (!data_) {
    throw errors::InputValidationException{
        fmt::format("Failed to construct regex match data buffer")};
  }
}

std::string_view Regex::Match::group(const std::string_view subject,
                                     const std::size_t groupNum) const {
  // Preconditions.
  // Not a moved-from object.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(data_);
  // Group number is in valid range.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(groupNum < pcre2_get_ovector_count(data_.get()));

  const PCRE2_SIZE* matches = pcre2_get_ovector_pointer(data_.get());

  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-pointer-arithmetic)
  const std::size_t startIdx = matches[groupNum * 2];
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-pointer-arithmetic)
  const std::size_t onePastEndIdx = matches[(groupNum * 2) + 1];
  // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-array-to-pointer-decay)
  assert(subject.size() >= onePastEndIdx);
  return subject.substr(startIdx, onePastEndIdx - startIdx);
}
}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
