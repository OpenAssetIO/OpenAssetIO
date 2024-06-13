// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <fmt/format.h>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(errors, BatchElementError)
OPENASSETIO_FWD_DECLARE(EntityReference)
OPENASSETIO_FWD_DECLARE(Context)
OPENASSETIO_FWD_DECLARE(hostApi, Manager)
OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(trait, TraitsData)

// Provide fmt formatters for most OpenAssetIO types.
// Whilst this is internal, it is implementation for public behaviour, such
// as << operators and python `str` and `repr`

template <>
struct fmt::formatter<openassetio::EntityReference> : fmt::formatter<string_view> {
  auto format(const openassetio::EntityReference& entityRef, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::EntityReferences> : fmt::formatter<string_view> {
  auto format(const openassetio::EntityReferences& entityRefs, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::StrMap> : fmt::formatter<string_view> {
  auto format(const openassetio::StrMap& strMap, format_context& ctx) const -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::managerApi::ManagerInterface::Capability>
    : fmt::formatter<string_view> {
  auto format(openassetio::managerApi::ManagerInterface::Capability capability,
              format_context& ctx) const -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::hostApi::Manager::Capability> : fmt::formatter<string_view> {
  auto format(openassetio::hostApi::Manager::Capability capability, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::errors::BatchElementError::ErrorCode>
    : fmt::formatter<string_view> {
  auto format(openassetio::errors::BatchElementError::ErrorCode errorCode,
              format_context& ctx) const -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::errors::BatchElementError> : fmt::formatter<string_view> {
  auto format(const openassetio::errors::BatchElementError& ber, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::TraitSet> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::TraitSet& traitSet, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::TraitSets> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::TraitSets& traitSets, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::InfoDictionary> : fmt::formatter<string_view> {
  auto format(const openassetio::InfoDictionary& infoDict, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::property::Value> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::property::Value& val, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::ContextPtr> : fmt::formatter<string_view> {
  auto format(const openassetio::ContextPtr& context, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::ContextConstPtr> : fmt::formatter<string_view> {
  auto format(const openassetio::ContextConstPtr& context, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::Context> : fmt::formatter<string_view> {
  auto format(const openassetio::Context& context, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::TraitsDataPtr> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::TraitsDataPtr& traitsData, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::TraitsDataConstPtr> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::TraitsDataConstPtr& traitsData, format_context& ctx) const
      -> decltype(ctx.out());
};

template <>
struct fmt::formatter<openassetio::trait::TraitsData> : fmt::formatter<string_view> {
  auto format(const openassetio::trait::TraitsData& traitsData, format_context& ctx) const
      -> decltype(ctx.out());
};
