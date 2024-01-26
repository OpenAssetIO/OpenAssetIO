// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include "Regex.hpp"

#include <cassert>

#include <fmt/format.h>

#include <openassetio/errors/exceptions.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {

namespace {
constexpr Str::size_type kErrorMessageMaxLength = 1000;

Str errorCodeToMessage(int errorCode) {
  Str errorMessage(kErrorMessageMaxLength, '\0');
  const auto errorMessageLength = pcre2_get_error_message(
      errorCode, reinterpret_cast<PCRE2_UCHAR8*>(errorMessage.data()), errorMessage.size());
  errorMessage.resize(static_cast<Str::size_type>(errorMessageLength));
  return errorMessage;
}
}  // namespace

Regex::Regex(const std::string_view pattern) {
  int errorCode;
  std::size_t errorOffset;

  code_ = pcre2_compile(
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

  const int numMatches =
      pcre2_jit_match(code_,                                         /* regex object */
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

  int numSubstitutions =
      pcre2_substitute(code_,                                         /* regex object */
                       reinterpret_cast<PCRE2_SPTR8>(subject.data()), /* subject */
                       subject.size(),                                /* length of subject */
                       0,                         /* start at offset 0 in the subject */
                       PCRE2_SUBSTITUTE_GLOBAL,   /* substitute all matches */
                       Match{code_}.data().get(), /* block for storing the result */
                       nullptr,                   /* use default match context */
                       reinterpret_cast<PCRE2_SPTR8>(replacement.data()), /* replacement */
                       replacement.size(),                                /* replacement length */
                       reinterpret_cast<PCRE2_UCHAR8*>(result.data()),    /* output buffer */
                       &resultSize                                        /* output buffer size */
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
  // Precondition.
  assert(groupNum < pcre2_get_ovector_count(data_.get()));

  PCRE2_SIZE* matches = pcre2_get_ovector_pointer(data_.get());

  const std::size_t startIdx = matches[groupNum * 2];
  const std::size_t onePastEndIdx = matches[groupNum * 2 + 1];
  assert(subject.size() >= onePastEndIdx);
  return subject.substr(startIdx, onePastEndIdx - startIdx);
}
}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
