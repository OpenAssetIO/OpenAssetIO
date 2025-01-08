// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include "formatter.hpp"

#include <algorithm>
#include <cstddef>
#include <iterator>
#include <string>
#include <variant>
#include <vector>

#include <fmt/core.h>
#include <fmt/format.h>

#include <openassetio/Context.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>
#include <openassetio/typedefs.hpp>

#include "../errors/exceptionMessages.hpp"

auto fmt::formatter<openassetio::EntityReference>::format(
    const openassetio::EntityReference& entityRef, format_context& ctx) const
    -> decltype(ctx.out()) {
  return formatter<string_view>::format(fmt::format("{}", entityRef.toString()), ctx);
}

auto fmt::formatter<openassetio::EntityReferences>::format(
    const openassetio::EntityReferences& entityRefs, format_context& ctx) const
    -> decltype(ctx.out()) {
  std::string result;

  if (entityRefs.empty()) {
    result = "[]";
  } else {
    result += "['";
    result += fmt::format("{}", join(entityRefs, "', '"));
    result += "']";
  }

  return formatter<string_view>::format(result, ctx);
}

auto fmt::formatter<openassetio::StrMap>::format(const openassetio::StrMap& strMap,
                                                 format_context& ctx) const
    -> decltype(ctx.out()) {
  std::vector<std::string> flattenedStrMap;
  flattenedStrMap.reserve(
      strMap.size());  // Reserve space for the elements to avoid multiple allocations

  for (const auto& [key, value] : strMap) {
    // Format each key-value pair into a single string
    flattenedStrMap.push_back(fmt::format("'{}': '{}'", key, value));
  }

  return formatter<string_view>::format(fmt::format("{{{}}}", join(flattenedStrMap, ", ")), ctx);
}

auto fmt::formatter<openassetio::managerApi::ManagerInterface::Capability>::format(
    openassetio::managerApi::ManagerInterface::Capability capability, format_context& ctx) const
    -> decltype(ctx.out()) {
  // Use checked access (.at()) since `capability` might come from a
  // buggy external source (e.g. bad static_cast from an int).
  return formatter<string_view>::format(
      openassetio::managerApi::ManagerInterface::kCapabilityNames.at(
          static_cast<std::size_t>(capability)),
      ctx);
}

auto fmt::formatter<openassetio::hostApi::Manager::Capability>::format(
    openassetio::hostApi::Manager::Capability capability, format_context& ctx) const
    -> decltype(ctx.out()) {
  // Use checked access (.at()) since `capability` might come from a
  // buggy external source (e.g. bad static_cast from an int).
  return formatter<string_view>::format(
      openassetio::managerApi::ManagerInterface::kCapabilityNames.at(
          static_cast<std::size_t>(capability)),
      ctx);
}

auto fmt::formatter<openassetio::errors::BatchElementError::ErrorCode>::format(
    const openassetio::errors::BatchElementError::ErrorCode errorCode, format_context& ctx) const
    -> decltype(ctx.out()) {
  return formatter<string_view>::format(errorCodeName(errorCode), ctx);
}

auto fmt::formatter<openassetio::errors::BatchElementError>::format(
    const openassetio::errors::BatchElementError& ber, format_context& ctx) const
    -> decltype(ctx.out()) {
  const openassetio::Str out = fmt::format("{}: {}", ber.code, ber.message);
  return formatter<string_view>::format(out, ctx);
}

auto fmt::formatter<openassetio::trait::TraitSet>::format(
    const openassetio::trait::TraitSet& traitSet, format_context& ctx) const
    -> decltype(ctx.out()) {
  std::vector<std::string> quotedTraitSet;
  quotedTraitSet.reserve(traitSet.size());
  std::transform(traitSet.cbegin(), traitSet.cend(), std::back_inserter(quotedTraitSet),
                 [](const std::string& trait) { return fmt::format("'{}'", trait); });

  return formatter<string_view>::format(fmt::format("{{{}}}", join(quotedTraitSet, ", ")), ctx);
}

auto fmt::formatter<openassetio::trait::TraitSets>::format(
    const openassetio::trait::TraitSets& traitSets, format_context& ctx) const
    -> decltype(ctx.out()) {
  return formatter<string_view>::format(fmt::format("[{}]", join(traitSets, ", ")), ctx);
}

namespace {
struct ToStringVisitor {
  std::string operator()(const openassetio::Str& arg) const { return fmt::format("'{}'", arg); }
  std::string operator()(const openassetio::Float arg) const { return std::to_string(arg); }
  std::string operator()(const openassetio::Int arg) const { return std::to_string(arg); }
  std::string operator()(const openassetio::Bool arg) const { return arg ? "True" : "False"; }
};
}  // namespace

auto fmt::formatter<openassetio::trait::property::Value>::format(
    const openassetio::trait::property::Value& val, format_context& ctx) const
    -> decltype(ctx.out()) {
  return formatter<string_view>::format(std::visit(ToStringVisitor(), val), ctx);
}

auto fmt::formatter<openassetio::InfoDictionary>::format(
    const openassetio::InfoDictionary& infoDict, format_context& ctx) const
    -> decltype(ctx.out()) {
  std::vector<std::string> flattenedStrMap;
  flattenedStrMap.reserve(
      infoDict.size());  // Reserve space for the elements to avoid multiple allocations

  for (const auto& [key, value] : infoDict) {
    // Format each key-value pair into a single string
    flattenedStrMap.push_back(fmt::format("'{}': {}", key, std::visit(ToStringVisitor(), value)));
  }

  return formatter<string_view>::format(fmt::format("{{{}}}", join(flattenedStrMap, ", ")), ctx);
}

auto fmt::formatter<openassetio::ContextPtr>::format(const openassetio::ContextPtr& context,
                                                     format_context& ctx) const
    -> decltype(ctx.out()) {
  if (context == nullptr) {
    return formatter<string_view>::format("null", ctx);
  }
  constexpr formatter<openassetio::Context> kValueFormatter;
  return kValueFormatter.format(*context, ctx);
}

auto fmt::formatter<openassetio::ContextConstPtr>::format(
    const openassetio::ContextConstPtr& context, format_context& ctx) const
    -> decltype(ctx.out()) {
  if (context == nullptr) {
    return formatter<string_view>::format("null", ctx);
  }
  constexpr formatter<openassetio::Context> kValueFormatter;
  return kValueFormatter.format(*context, ctx);
}

auto fmt::formatter<openassetio::Context>::format(const openassetio::Context& context,
                                                  format_context& ctx) const
    -> decltype(ctx.out()) {
  const openassetio::Str out = fmt::format("{{'locale': {}, 'managerState': {}}}", context.locale,
                                           static_cast<void*>(context.managerState.get()));

  return formatter<string_view>::format(out, ctx);
}

auto fmt::formatter<openassetio::trait::TraitsDataPtr>::format(
    const openassetio::trait::TraitsDataPtr& traitsData, format_context& ctx) const
    -> decltype(ctx.out()) {
  if (traitsData == nullptr) {
    return formatter<string_view>::format("null", ctx);
  }
  constexpr formatter<openassetio::trait::TraitsData> kValueFormatter;
  return kValueFormatter.format(*traitsData, ctx);
}

auto fmt::formatter<openassetio::trait::TraitsDataConstPtr>::format(
    const openassetio::trait::TraitsDataConstPtr& traitsData, format_context& ctx) const
    -> decltype(ctx.out()) {
  if (traitsData == nullptr) {
    return formatter<string_view>::format("null", ctx);
  }
  constexpr formatter<openassetio::trait::TraitsData> kValueFormatter;
  return kValueFormatter.format(*traitsData, ctx);
}

auto fmt::formatter<openassetio::trait::TraitsData>::format(
    const openassetio::trait::TraitsData& traitsData, format_context& ctx) const
    -> decltype(ctx.out()) {
  const auto traitSet = traitsData.traitSet();
  std::vector<openassetio::Str> traitStrings;
  traitStrings.reserve(traitSet.size());

  for (const auto& traitId : traitSet) {
    std::vector<std::string> propertyStrings;
    const auto keys = traitsData.traitPropertyKeys(traitId);
    std::transform(std::cbegin(keys), std::cend(keys), std::back_inserter(propertyStrings),
                   [&traitsData, &traitId](const std::string& propertyKey) {
                     openassetio::trait::property::Value out;
                     traitsData.getTraitProperty(&out, traitId, propertyKey);
                     return fmt::format(R"('{}': {})", propertyKey, out);
                   });

    // Add the string that makes up the trait, which is the dict section for the traitId,
    // followed by all the property key value pairs.
    traitStrings.push_back(fmt::format("'{}': {{{}}}", traitId, join(propertyStrings, ", ")));
  }

  // The idea here being that this is a valid python dict, hence all the extra brace formatting
  return formatter<string_view>::format(fmt::format("{{{}}}", join(traitStrings, ", ")), ctx);
}
