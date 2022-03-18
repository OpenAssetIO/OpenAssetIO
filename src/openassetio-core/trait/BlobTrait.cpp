// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <utility>

#include <openassetio/trait/BlobTrait.hpp>
#include <openassetio/trait/property.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace trait {

namespace {
/// Key for a URL property.
const property::Key kUrl{"url"};
/// Key for a mime type property.
const property::Key kMimeType{"mimeType"};
}  // namespace

TraitPropertyStatus BlobTrait::getUrl(property::Str* out) const {
  return getTraitProperty(out, kId, kUrl);
}

void BlobTrait::setUrl(property::Str url) {
  specification()->setTraitProperty(kId, kUrl, std::move(url));
}

TraitPropertyStatus BlobTrait::getMimeType(property::Str* out) const {
  return getTraitProperty(out, kId, kMimeType);
}

void BlobTrait::setMimeType(property::Str mimeType) {
  specification()->setTraitProperty(kId, kMimeType, std::move(mimeType));
}

}  // namespace trait
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
