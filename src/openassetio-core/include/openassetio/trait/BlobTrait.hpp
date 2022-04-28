// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Define the core `BlobTrait` trait class.
 */
#pragma once

#include <openassetio/export.h>

#include "TraitBase.hpp"

#include "property.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace trait {

/**
 * Core trait class representing a locatable blob of data of a specific
 * type.
 *
 * Has the ID of "blob" and defines "url" and "mimeType" properties.
 *
 * This core trait defines one of the most common set of properties in
 * the specification::Specification of an @ref entity - specifically, a
 * URL and data (MIME) type.
 *
 * For example, the URL can be a local file system path (i.e.
 * `file:///`). Thus the common workflow of @ref resolve "resolving" an
 * @ref entity_reference to a file path is likely to involve the host
 * requesting, and the manager returning, a @ref
 * specification::Specification "Specification" supporting this
 * `BlobTrait`.
 *
 * @see TraitBase
 * @see specification::Specification
 */
struct OPENASSETIO_CORE_EXPORT BlobTrait : TraitBase<BlobTrait> {
  /// ID of this trait.
  static inline const TraitId kId{"blob"};

  /// Hoist base class constructor.
  using TraitBase<BlobTrait>::TraitBase;

  /**
   * Get the URL property for this trait from the wrapped specification.
   *
   * @param[out] out Storage for value, if property is set.
   * @return `true` if property is set, `false` otherwise.
   * @exception `std::out_of_range` if this trait is not supported by
   * the wrapped specification.
   */
  [[nodiscard]] TraitPropertyStatus getUrl(Str* out) const;

  /**
   * Set the URL property for this trait in the wrapped specification.
   *
   * @param url URL value to set.
   * @exception `std::out_of_range` if this trait is not supported by
   * the wrapped specification.
   */
  void setUrl(Str url);

  /**
   * Get the mime type property for this trait from the wrapped
   * specification.
   *
   * @param[out] out Storage for value, if property is set.
   * @return `true` if property is set, `false` otherwise.
   * @exception `std::out_of_range` if this trait is not supported by
   * the wrapped specification.
   */
  [[nodiscard]] TraitPropertyStatus getMimeType(Str* out) const;

  /**
   * Set the mime type property for this trait in the wrapped
   * specification.
   *
   * @param mimeType Mime type value to set.
   * @exception `std::out_of_range` if this trait is not supported by
   * the wrapped specification.
   */
  void setMimeType(Str mimeType);
};
}  // namespace trait
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
