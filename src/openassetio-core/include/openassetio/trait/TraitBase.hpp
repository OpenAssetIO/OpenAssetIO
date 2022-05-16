// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Base class for all specification traits.
 */
#pragma once
#include <algorithm>
#include <memory>
#include <utility>

#include "../specification/Specification.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace trait {

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// TODO(TC): This class is currently untested as the concrete
// BlobTrait implementation has been removed from the core API (and
// migrated to OpenAssetIO-MediaCreation.
// It _has_ been tested in the past, but is no longer covered.
// When we move to the autogeneration of trait classes from a JSON
// schema, we need to ensure that any resulting reused API classes
// are properly tested.
// See: https://github.com/TheFoundryVisionmongers/OpenAssetIO/pull/358#discussion_r860709504
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

/**
 * Abstract CRTP base class for specification traits.
 *
 * A trait view provides a way to hide the underlying dictionary-like
 * data access from hosts and managers. Trait view classes wrap a
 * @ref specification::Specification "Specification" and provide member
 * functions that query/mutate properties on the specification.
 *
 * @see BlobTrait
 *
 * This non-virtual templated base class provides the common interface
 * for a concrete trait view.
 *
 * As an example, assume a trait view called `MyTrait` and an arbitrary
 * specification. Before we can extract `MyTrait` property values from
 * the specification we must check that it supports `MyTrait`. We can
 * then use the trait's concrete accessors to retrieve data from the
 * underlying dictionary-like specification. Usage may thus look
 * something like
 *
 *     property::Int myValue = 123;  // Default if property not found.
 *
 *     MyTrait myTrait{specification};
 *
 *     if (myTrait.isValid()) {
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
 * @warning The `kId` member must be `inline` to support @ref
 * specification::Specification "specifications" that statically
 * construct their list of supported trait IDs. This is to avoid the
 * so-called _Static Initialization Order Fiasco_, when a
 * specification's static trait list is constructed using static trait
 * IDs.
 *
 * In addition, the derived class should implement appropriate typed
 * accessor / mutator methods that internally call the wrapped
 * specification's @ref specification::Specification::getTraitProperty
 * "getTraitProperty" / @ref
 * specification::Specification::setTraitProperty "setTraitProperty".
 *
 * Such accessor/mutator functions then provide developers with
 * compile-time checks and IDE code-completion, which would not be
 * available with arbitrary string-based lookups.
 *
 * @note Attempting to access a trait's properties without first
 * ensuring the specification supports that trait via `isValid`, or
 * otherwise, may trigger a `std::out_of_range` exception if the trait
 * is not supported by the specification.
 *
 * @tparam Derived Concrete subclass.
 */
template <class Derived>
struct TraitBase {
  /// Ref-counted smart pointer to underlying Specification.
  using SpecificationPtr = std::shared_ptr<specification::Specification>;

  /**
   * Construct this trait view, wrapping the given specification.
   *
   * @param specification Underlying specification to wrap.
   */
  explicit TraitBase(SpecificationPtr specification) : specification_{std::move(specification)} {}

  /**
   * Check whether the specification this trait has been applied to
   * actually supports this trait.
   *
   * @return `true` if the underlying specification supports this trait,
   * `false` otherwise.
   **/
  [[nodiscard]] bool isValid() const { return specification_->hasTrait(Derived::kId); }

  /**
   * Applies this trait to the specification.
   *
   * If the specification already has this trait, it is a no-op.
   **/
  void imbue() const { specification_->addTrait(Derived::kId); }

  /**
   * Applies this trait to the supplied specification.
   *
   * If the specification already has this trait, it is a no-op.
   *
   * @param specification The specification to apply the trait to.
   **/
  static void imbueTo(const SpecificationPtr& specification) {
    specification->addTrait(Derived::kId);
  }

 protected:
  /**
   * Get the underlying specification that this trait is wrapping.
   *
   * @return Wrapped Specification.
   */
  SpecificationPtr& specification() { return specification_; }

  /**
   * Get the underlying specification that this trait is wrapping.
   *
   * @return Wrapped Specification.
   */
  [[nodiscard]] const SpecificationPtr& specification() const { return specification_; }

  /**
   * Convenience typed accessor to properties in the underlying
   * specification.
   *
   * @tparam T Type to extract from variant property.
   * @param[out] out Storage for value, if property is set.
   * @param traitId ID of trait to query.
   * @param propertyKey Key of property to query.
   * @return Status of property in the specification.
   */
  template <class T>
  [[nodiscard]] TraitPropertyStatus getTraitProperty(T* out, const TraitId& traitId,
                                                     const property::Key& propertyKey) const {
    if (property::Value value; specification()->getTraitProperty(&value, traitId, propertyKey)) {
      if (T* maybeOut = std::get_if<T>(&value)) {
        *out = *maybeOut;
        return TraitPropertyStatus::kFound;
      }
      return TraitPropertyStatus::kInvalidValue;
    }
    return TraitPropertyStatus::kMissing;
  }

 private:
  SpecificationPtr specification_;
};
}  // namespace trait
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
