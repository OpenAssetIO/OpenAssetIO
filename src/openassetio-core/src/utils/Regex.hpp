// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once
#include <cstddef>
#include <memory>
#include <optional>
#include <string_view>

#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace utils {

/**
 * Regular expression compilation, matching and caching.
 *
 * Wraps PCRE2, using its JIT compilation and matching functions.
 */
class Regex {
 public:
  /**
   * Container for a regex match.
   */
  class Match {
    struct MatchDataDeleter {
      void operator()(pcre2_match_data* ptr) { pcre2_match_data_free(ptr); }
    };
    using Data = std::unique_ptr<pcre2_match_data, MatchDataDeleter>;

   public:
    explicit Match(const pcre2_code* code);

    ~Match() = default;
    Match(const Match&) = delete;
    // Move must be defined to wrap in std::optional. Note that it will
    // leave the moved-from object in an invalid state.
    Match(Match&&) noexcept = default;
    Match& operator=(const Match&) = delete;
    Match& operator=(Match&&) noexcept = delete;

    /**
     * Get the string from a group in the match.
     *
     * Warning: no validation is performed. It is assumed the given
     * group number exists in the match data.
     *
     * @param subject Subject string to extract a substring view from.
     * Should be the same as the subject of the original `match`
     * call, or at least a string of equal length.
     *
     * @param groupNum Regex capture group to extract.
     *
     * @return Substring view of the match in the subject string.
     */
    [[nodiscard]] std::string_view group(std::string_view subject, std::size_t groupNum) const;

    /**
     * Get the internal match data pointer.
     *
     * @return Internal PCRE2 match data.
     */
    [[nodiscard]] const Data& data() const { return data_; }

   private:
    Data data_;
  };

  /**
   * Constructor.
   *
   * Pre-compiles the regular expression pattern.
   *
   * Note that:
   * - Patterns are case-insensitive.
   * - `$` matches end of string, not newline.
   * - `.` matches all characters, including newlines.
   *
   * @param pattern Regex pattern.
   */
  explicit Regex(std::string_view pattern);

  ~Regex();
  Regex(const Regex& other) = delete;
  Regex(Regex&& other) noexcept = delete;
  Regex& operator=(const Regex& other) = delete;
  Regex& operator=(Regex&& other) noexcept = delete;

  /**
   * Check if the regex matches a given subject string.
   *
   * Caches the match results for subsequent retrieval in other methods.
   *
   * @param subject Subject string to match the regex against.
   *
   * @return `true` if there is a match, `false` otherwise.
   */
  [[nodiscard]] std::optional<Match> match(std::string_view subject) const;

  /**
   * Get a new string with all matches of the regex substituted with the
   * given replacement string.
   *
   * Resulting string must be less than or equal in size to the subject
   * string.
   *
   * @param subject String to copy, with substitutions.
   * @param replacement Replacement to substitute matches with.
   * @return New string that is a copy of @p subject but with matches
   * replaced with @p replacement.
   * @throws InputValidationException On substitution error (e.g. if the
   * resulting string would be longer than the subject string).
   */
  [[nodiscard]] Str substituteToReduceSize(const std::string_view& subject,
                                           const std::string_view& replacement) const;

 private:
  pcre2_code* code_{nullptr};
};
}  // namespace utils
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
