// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Typedefs for the trait property data stored within specifications.
 */
#pragma once

#include <set>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/trait/property.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(trait, TraitsData)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace trait {
/**
 * A collection of trait IDs
 *
 * ID collections are a set, rather than a list. In that,
 * no single ID can appear more than once and the order of the IDs
 * has no meaning and is not preserved.
 */
using TraitSet = std::set<TraitId>;

/**
 * An ordered list of trait sets.
 */
using TraitSets = std::vector<TraitSet>;

/**
 * An ordered list of @fqref{trait.TraitsData} "TraitsData" instances.
 */
using TraitsDatas = std::vector<TraitsDataPtr>;
}  // namespace trait
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
