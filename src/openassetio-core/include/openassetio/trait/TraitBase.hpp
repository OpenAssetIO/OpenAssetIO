// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Base class for all specification traits.
 */
#pragma once
#include <algorithm>
#include <memory>
#include <utility>

#include "../TraitsData.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace trait {

/**
 * Abstract CRTP base class for specification traits.
 *
 * A trait view provides a way to hide the underlying dictionary-like
 * data access from hosts and managers. Trait view classes wrap a
 * @ref TraitsData "TraitsData" and provide member functions that
 * query/mutate properties of the data.
 *
 * @see @ref entities_traits_and_specifications
 *
 * This non-virtual templated base class provides the common interface
 * for a concrete trait view.
 *
 * As an example, assume a trait view called `MyTrait` and an arbitrary
 * data instance. Before we can extract `MyTrait` property values from
 * the data we must check that it supports `MyTrait`. We can
 * then use the trait's concrete accessors to retrieve values from the
 * underlying dictionary-like @fqref{TraitsData} "TraitsData" instance.
 * Usage may thus look something like
 *
 *     property::Int myValue = 123;  // Default if property not found.
 *
 *     MyTrait myTrait{traitsData};
 *
 *     if (myTrait.isImbued()) {
 *
 *       if (myTrait.getMyValue(&myValue) != TraitPropertyStatus::kFound) {
 *
 *         std::cerr << "Warning: myValue not found\n";
 *       }
 *     }
 *
 * A trait class inheriting from this base must have a
 * `static inline TraitId kId` member giving the unique string ID of
 * that trait.
 *
 * @see TraitId
 *
 * @warning The `kId` member must be `inline` to support @needsref
 * specifications that statically construct their list of supported
 * trait IDs. This is to avoid the so-called _Static Initialization
 * Order Fiasco_, when a specification's static trait list is
 * constructed using static trait IDs.
 *
 * In addition, the derived class should implement appropriate typed
 * accessor / mutator methods that internally call the wrapped
 * data's @ref TraitsData::getTraitProperty
 * "getTraitProperty" / @ref TraitsData::setTraitProperty
 * "setTraitProperty".
 *
 * Such accessor/mutator functions then provide developers with
 * compile-time checks and IDE code-completion, which would not be
 * available with arbitrary string-based lookups.
 *
 * @note Attempting to access a trait's properties without first
 * ensuring the underlying TraitsData instance has that trait via
 * `isImbued`, or otherwise, may trigger a `std::out_of_range` exception
 * if the trait is not set.
 *
 * @tparam Derived Concrete subclass.
 */
template <class Derived>
struct TraitBase {
  /**
   * Construct this trait view, wrapping the given TraitsData instance.
   *
   * @param data The instance to wrap.
   */
  explicit TraitBase(TraitsDataPtr data) : data_{std::move(data)} {}

  /**
   * Check whether a TraitsData instance has this trait set.
   *
   * @param data Data to check.
   * @return `true` if the given TraitsData instance has this trait
   * set, `false` otherwise.
   */
  [[nodiscard]] static bool isImbuedTo(const TraitsDataPtr& data) {
    return data->hasTrait(Derived::kId);
  }

  /**
   * Check whether the TraitsData instance this trait has been
   * constructed with has this trait set.
   *
   * @return `true` if the underlying TraitsData instance has this trait
   * set, `false` otherwise.
   **/
  [[nodiscard]] bool isImbued() const { return isImbuedTo(data_); }

  /**
   * Applies this trait to the wrapped TraitsData instance.
   *
   * If the instance already has this trait, it is a no-op.
   **/
  void imbue() const { data_->addTrait(Derived::kId); }

  /**
   * Applies this trait to the supplied TraitsData instance.
   *
   * If the instance already has this trait, it is a no-op.
   *
   * @param data The instance to apply the trait to.
   **/
  static void imbueTo(const TraitsDataPtr& data) { data->addTrait(Derived::kId); }

 protected:
  /**
   * Get the underlying data that this trait is wrapping.
   *
   * @return Wrapped TraitsData.
   */
  TraitsDataPtr& data() { return data_; }

  /**
   * Get the underlying data that this trait is wrapping.
   *
   * @return Wrapped TraitsData.
   */
  [[nodiscard]] const TraitsDataPtr& data() const { return data_; }

  /**
   * Convenience typed accessor to properties in the underlying
   * data.
   *
   * @tparam T Type to extract from variant property.
   * @param[out] out Storage for value, if property is set.
   * @param traitId ID of trait to query.
   * @param propertyKey Key of property to query.
   * @return Status of property in the underlying data.
   */
  template <class T>
  TraitPropertyStatus getTraitProperty(T* out, const TraitId& traitId,
                                       const property::Key& propertyKey) const {
    if (property::Value value; data()->getTraitProperty(&value, traitId, propertyKey)) {
      if (T* maybeOut = std::get_if<T>(&value)) {
        *out = *maybeOut;
        return TraitPropertyStatus::kFound;
      }
      return TraitPropertyStatus::kInvalidValue;
    }
    return TraitPropertyStatus::kMissing;
  }

 private:
  TraitsDataPtr data_;
};
}  // namespace trait
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
