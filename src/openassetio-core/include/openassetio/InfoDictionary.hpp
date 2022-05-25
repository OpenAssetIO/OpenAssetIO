// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <unordered_map>
#include <variant>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/// Types available as values in a InfoDictionary.
using InfoDictionaryValue = std::variant<Bool, Int, Float, Str>;
/**
 * Dictionary type used for @fqref{managerAPI::ManagerInterface::info}
 * "ManagerInterface::info".
 */
using InfoDictionary = std::unordered_map<Str, InfoDictionaryValue>;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
