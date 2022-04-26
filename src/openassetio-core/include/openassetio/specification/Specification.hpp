// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Provide the base dynamic specification class.
 */
#pragma once

#include <memory>
#include <unordered_set>

#include <openassetio/export.h>

#include "../trait/property.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
/**
 * Comprises the base Specification class and concrete classes of core
 * specifications derived from it.
 */
namespace specification {

/**
 * Structure for data exchange between a @ref host and a @ref
 * manager.
 *
 * A specification is logically a set of supported @needsref trait
 * "traits", each identified by a unique string, plus optional
 * key-value properties associated with each of those traits.
 *
 * Trait @ref trait::property::Key "property keys" are always strings.
 * Property values are strings, integers, floating point, or booleans.
 * Any of a trait's properties can be legitimately left unset - it is up
 * to the consumer (host or manager, depending on the API method) to
 * decide how this should be handled.
 *
 * @todo Add SimpleMap trait property value type.
 *
 * @see trait::property
 *
 * Various API methods require a populated specification to be provided
 * by the host, which the manager can interrogate in order to determine
 * the correct response.
 *
 * Conversely, various API methods, in particular @needsref
 * ManagerInterface::resolve, require the manager to return a
 * populated specification to the host. The traits (and hence their
 * properties) contained within the returned specification are
 * determined by the intersection of the traits that were requested by
 * the host and the traits that the manager supports.
 *
 * Since specifications are generic dictionary-like data structures,
 * accurate data access/mutation relies on well-known trait IDs and
 * property names. This introduces a possible avenue for user error due
 * to misspelling, as well as difficulty in discovering what properties
 * may be available for a given trait.
 *
 * Therefore, it is strongly advised that accessing and mutating trait
 * properties is performed using trait view wrapper classes wherever
 * possible, rather than directly using the accessor/mutator functions
 * on the specification.
 *
 * @see trait::TraitBase
 *
 */
class OPENASSETIO_CORE_EXPORT Specification {
 public:
  /**
   * A collection of supported trait IDs
   *
   * ID collections are a set, rather than a list. In that,
   * no single ID can appear more than once and the order of the IDs
   * has no meaning and is not preserved.
   */
  using TraitIds = std::unordered_set<trait::TraitId>;

  /**
   * Construct such that this specification has the given set of
   * trait IDs.
   *
   * @param traitIds The consituent traits IDs.
   */
  explicit Specification(const TraitIds& traitIds);

  /**
   * Defaulted virtual destructor establishing this as a base class
   * for more concrete specifications.
   */
  virtual ~Specification();

  /**
   * Return the trait ID's held by the specification.
   */
  [[nodiscard]] TraitIds traitIds() const;

  /**
   * Return whether this specification has the given trait.
   *
   * @param traitId ID of trait to check for.
   * @return `true` if trait is present, `false` otherwise.
   */
  [[nodiscard]] bool hasTrait(const trait::TraitId& traitId) const;

  /**
   * Get the value of a given trait property, if the property has
   * been set.
   *
   * @param[out] out Storage for result, only written to if the property
   * is set.
   * @param traitId ID of trait to query.
   * @param propertyKey Key of trait's property to query.
   * @return `true` if value was found, `false` if it is unset.
   * @exception `std::out_of_range` if the specification does not have
   * this trait.
   */
  [[nodiscard]] bool getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
                                      const trait::property::Key& propertyKey) const;

  /**
   * Set the value of given trait property.
   *
   * @param traitId ID of trait to update.
   * @param propertyKey Key of property to set.
   * @param propertyValue Value to set.
   * @exception `std::out_of_range` if the specification does not have
   * this trait.
   */
  void setTraitProperty(const trait::TraitId& traitId, const trait::property::Key& propertyKey,
                        trait::property::Value propertyValue);

  /**
   * Compares specifications based on their trait and property values.
   *
   * @param other The specification to compare to.
   */
  bool operator==(const Specification& other) const;

 private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};
}  // namespace specification
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
