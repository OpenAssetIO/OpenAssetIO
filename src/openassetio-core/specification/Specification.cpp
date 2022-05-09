// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/specification/Specification.hpp>
#include <unordered_map>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace specification {

class Specification::Impl {
 public:
  Impl() = default;

  explicit Impl(const TraitIds& traitIds) { addTraits(traitIds); }
  ~Impl() = default;

  TraitIds traitIds() const {
    TraitIds ids;
    ids.reserve(data_.size());
    for (const auto& item : data_) {
      ids.insert(item.first);
    }
    return ids;
  }

  bool hasTrait(const trait::TraitId& traitId) const {
    return static_cast<bool>(data_.count(traitId));
  }

  void addTrait(const trait::TraitId& traitId) { data_[traitId]; }

  void addTraits(const TraitIds& traitIds) {
    for (const auto& traitId : traitIds) {
      data_[traitId];
    }
  }

  bool getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
                        const trait::property::Key& propertyKey) const {
    // Use `at` deliberately to trigger exception if trait doesn't exist
    const auto& traitDict = data_.at(traitId);

    const auto& iter = traitDict.find(propertyKey);
    if (iter == traitDict.end()) {
      return false;
    }
    *out = iter->second;
    return true;
  }

  void setTraitProperty(const trait::TraitId& traitId, const trait::property::Key& propertyKey,
                        trait::property::Value propertyValue) {
    // Use `at` deliberately to trigger exception if trait doesn't exist
    data_.at(traitId)[propertyKey] = std::move(propertyValue);
  }

  bool operator==(const Impl& other) const { return data_ == other.data_; }

 private:
  using Properties = std::unordered_map<trait::property::Key, trait::property::Value>;
  using PropertiesByTrait = std::unordered_map<trait::TraitId, Properties>;
  PropertiesByTrait data_;
};

Specification::Specification() : impl_{std::make_unique<Impl>()} {}

Specification::Specification(const TraitIds& traitIds) : impl_{std::make_unique<Impl>(traitIds)} {}

Specification::~Specification() = default;

Specification::TraitIds Specification::traitIds() const { return impl_->traitIds(); }

void Specification::addTrait(const trait::TraitId& traitId) { impl_->addTrait(traitId); }

void Specification::addTraits(const TraitIds& traitIds) { impl_->addTraits(traitIds); }

bool Specification::hasTrait(const trait::TraitId& traitId) const {
  return impl_->hasTrait(traitId);
}

bool Specification::getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
                                     const trait::property::Key& propertyKey) const {
  return impl_->getTraitProperty(out, traitId, propertyKey);
}

void Specification::setTraitProperty(const trait::TraitId& traitId,
                                     const trait::property::Key& propertyKey,
                                     trait::property::Value propertyValue) {
  impl_->setTraitProperty(traitId, propertyKey, std::move(propertyValue));
}

bool Specification::operator==(const Specification& other) const { return *impl_ == *other.impl_; }
}  // namespace specification
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
