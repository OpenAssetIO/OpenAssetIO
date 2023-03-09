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
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
OPENASSETIO_DECLARE_PTR(TraitsData)

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
 * openassetio.TraitBase "Trait" derived "views" at runtime by a @ref
 * host or @ref manager to ensure consistent access to the correct keys.
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
   * Construct an empty instance, with no traits.
   */
  [[nodiscard]] static TraitsDataPtr make();

  /**
   * Construct such that this instance has the given set of traits.
   *
   * @param traitSet The constituent traits IDs.
   */
  [[nodiscard]] static TraitsDataPtr make(const trait::TraitSet& traitSet);

  /**
   * Construct such that this instance is a deep copy of the other.
   *
   * @param other The instance to copy.
   */
  [[nodiscard]] static TraitsDataPtr make(const TraitsDataConstPtr& other);

  /**
   * Defaulted destructor.
   */
  ~TraitsData();

  /**
   * Return the trait IDs held by the instance.
   */
  [[nodiscard]] trait::TraitSet traitSet() const;

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
  void addTraits(const trait::TraitSet& traitSet);

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
  bool getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
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
   * Returns the properties set for a given trait.
   *
   * If the trait has not been given to this instance, or the trait has
   * no properties set, then it will return an empty set.
   */
  [[nodiscard]] trait::property::KeySet traitPropertyKeys(const trait::TraitId& traitId) const;

  /**
   * Compares instances based on their trait and property values.
   *
   * @param other The instance to compare to.
   */
  bool operator==(const TraitsData& other) const;

 private:
  TraitsData();
  explicit TraitsData(const trait::TraitSet& traitSet);
  TraitsData(const TraitsData& other);

  class Impl;
  std::unique_ptr<Impl> impl_;
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
