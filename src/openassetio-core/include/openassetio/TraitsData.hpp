// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 *  Provide the transport-level data container for trait sets and their
 *  property values.
 */
#pragma once

#include <memory>
#include <unordered_set>

#include <openassetio/export.h>

#include "trait/property.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * A transport-level container for data exchange between a @ref host and
 * a @ref manager.
 *
 * The @ref Specification system combines one or more @ref trait
 * "traits" into a @ref trait_set to classify concepts within the API.
 * Traits may define a number of simple-typed properties, allowing them
 * to be used to exchange data between interested parties.
 *
 * A key requirement of the traits system is to be fully run-time
 * extensible. Additional specifications and traits can be defined as
 * required by any particular API integration.
 *
 * This is accomplished by breaking the system into two components:
 *  - A simple, generic data container that holds a trait set and its
 *    properties.
 *  - Custom views on this container that provide strongly-typed access.
 *
 * TraitsData is the transport-layer container that holds a @ref
 * trait_set, and any values set for the properties of these traits.
 * It has no semantic understanding of the data, providing simple
 * "by name" set/get of traits and their properties.
 *
 * This allows easy serialization and exchange of this data between
 * languages and sub-systems using the low-level introspection
 * functionality provided by this class.
 *
 * As generic access to the container's data (based on
 * "well-known-strings") is inherently unstable. Instances of this class
 * should generally be wrapped in one of the specialized @ref
 * openassetio.SpecificationBase "Specification" or @ref
 * openassetio.Trait "Trait" derived "views" at runtime by a @ref host
 * or @ref manager to ensure consistent access to the correct keys.
 *
 * Trait @ref trait::property::Key "property keys" are always strings.
 * Property values are strings, integers, floating point, or booleans.
 * Any of a trait's properties can be legitimately left unset - it is up
 * to the consumer (host or manager, depending on the API method) to
 * decide how this should be handled.
 *
 * @todo Add InfoDictionary trait property value type.
 *
 * @see trait::property
 * @see @ref entities_traits_and_specifications
 */
class OPENASSETIO_CORE_EXPORT TraitsData final {
 public:
  /**
   * A collection of trait IDs
   *
   * ID collections are a set, rather than a list. In that,
   * no single ID can appear more than once and the order of the IDs
   * has no meaning and is not preserved.
   */
  using TraitSet = std::unordered_set<trait::TraitId>;

  /**
   * Construct an empty instance, with no traits.
   */
  TraitsData();

  /**
   * Construct such that this instance has the given set of traits.
   *
   * @param traitSet The consituent traits IDs.
   */
  explicit TraitsData(const TraitSet& traitSet);

  /**
   * Construct such that this instance is a deep copy of the other.
   *
   * @param other The instance to copy.
   */
  TraitsData(const TraitsData& other);

  /**
   * Defaulted destructor.
   */
  ~TraitsData();

  /**
   * Return the trait IDs held by the instance.
   */
  [[nodiscard]] TraitSet traitSet() const;

  /**
   * Return whether this instance has the given trait.
   *
   * @param traitId ID of trait to check for.
   * @return `true` if trait is present, `false` otherwise.
   */
  [[nodiscard]] bool hasTrait(const trait::TraitId& traitId) const;

  /**
   * Add the specified trait to this instance.
   *
   * If this instance already has this trait, it is a no-op.
   *
   * @param traitId ID of the trait to add.
   */
  void addTrait(const trait::TraitId& traitId);

  /**
   * Add the specified traits to this instance.
   *
   * If this instance already has any of the supplied traits, they
   * are skipped.
   *
   * @param traitSet A trait set with the traits to add.
   */
  void addTraits(const TraitSet& traitSet);

  /**
   * Get the value of a given trait property, if the property has
   * been set.
   *
   * @param[out] out Storage for result, only written to if the property
   * is set.
   * @param traitId ID of trait to query.
   * @param propertyKey Key of trait's property to query.
   * @return `true` if value was found, `false` if it is unset.
   * @exception `std::out_of_range` if this instance does not have
   * this trait.
   */
  [[nodiscard]] bool getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
                                      const trait::property::Key& propertyKey) const;

  /**
   * Set the value of given trait property.
   *
   * If the instance does not yet have this trait, it will be
   * added by this call.
   *
   * @param traitId ID of trait to update.
   * @param propertyKey Key of property to set.
   * @param propertyValue Value to set.
   */
  void setTraitProperty(const trait::TraitId& traitId, const trait::property::Key& propertyKey,
                        trait::property::Value propertyValue);

  /**
   * Compares instances based on their trait and property values.
   *
   * @param other The instance to compare to.
   */
  bool operator==(const TraitsData& other) const;

 private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

/// Ref-counted smart pointer to underlying TraitsData.
using TraitsDataPtr = std::shared_ptr<TraitsData>;
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
