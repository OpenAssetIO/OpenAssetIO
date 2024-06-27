// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <ostream>
#include <unordered_map>
#include <vector>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(Context)
OPENASSETIO_FWD_DECLARE(managerApi, HostSession)
OPENASSETIO_FWD_DECLARE(trait, TraitsData)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
class EntityReference;
using EntityReferences = std::vector<EntityReference>;

/**
 * Insertion operator for use with ostreams.
 * Formats as "an_entity_reference".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const EntityReference& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "['an_entity_reference_1', 'an_entity_reference_2']".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const EntityReferences& formattable);

/**
 * Insertion operator for use with ostreams.
 * Formats as "{'locale': {'aTrait': {'aProperty': propertyVal}}, 'managerState': memoryAddress}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out, const ContextPtr& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'locale': {'aTrait': {'aProperty': propertyVal}}, 'managerState': memoryAddress}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const ContextConstPtr& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'locale': {'aTrait': {'aProperty': propertyVal}}, 'managerState': memoryAddress}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out, const Context& formattable);

namespace managerApi {
/**
 * Insertion operator for use with ostreams.
 * Formats as "humanReadableCapabilityName".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const ManagerInterface::Capability& formattable);
}  // namespace managerApi

namespace hostApi {
/**
 * Insertion operator for use with ostreams.
 * Formats as "humanReadableCapabilityName".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const Manager::Capability& formattable);
}  // namespace hostApi

namespace errors {
/**
 * Insertion operator for use with ostreams.
 * Formats as "humanReadableErrorCodeName".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const BatchElementError::ErrorCode& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "humanReadableErrorCodeName: Error message.".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const BatchElementError& formattable);
}  // namespace errors

namespace trait {

/**
 * Insertion operator for use with ostreams.
 * Formats as "{'aTrait': {'aTraitProperty': traitValue, 'anotherTraitProperty':
 * anotherTraitValue}, 'anotherTrait': {aTraitProperty: traitValue}}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const TraitsDataPtr& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'aTrait': {'aTraitProperty': traitValue, 'anotherTraitProperty':
 * anotherTraitValue}, 'anotherTrait': {aTraitProperty: traitValue}}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out,
                                                 const TraitsDataConstPtr& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'aTrait': {'aTraitProperty': traitValue, 'anotherTraitProperty':
 * anotherTraitValue}, 'anotherTrait': {aTraitProperty: traitValue}}".
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out, const TraitsData& formattable);

namespace property {

/**
 * Insertion operator for use with ostreams.
 * Formats as "Value", (or "'Value'" if formattable is a string)
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(std::ostream& out, const Value& formattable);
}  // namespace property
}  // namespace trait
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

/* The types here are just typedefs to standard types, and thus must be defined
 * in the standard namespace. */
namespace std {
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'key1': 'value1', 'key2': 'value2'}"
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(
    std::ostream& out, const openassetio::OPENASSETIO_CORE_ABI_VERSION::StrMap& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'key1': value1, 'key2': value2}"
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(
    std::ostream& out,
    const openassetio::OPENASSETIO_CORE_ABI_VERSION::InfoDictionary& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "{'trait1', 'trait2'}"
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(
    std::ostream& out,
    const openassetio::OPENASSETIO_CORE_ABI_VERSION::trait::TraitSet& formattable);
/**
 * Insertion operator for use with ostreams.
 * Formats as "[{'trait1', 'trait2'}, {'trait3', 'trait4'}]"
 */
OPENASSETIO_CORE_EXPORT std::ostream& operator<<(
    std::ostream& out,
    const openassetio::OPENASSETIO_CORE_ABI_VERSION::trait::TraitSets& formattable);
}  // namespace std
