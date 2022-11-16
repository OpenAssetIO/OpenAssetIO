// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <unordered_map>

#include <openassetio/TraitsData.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
class TraitsData::Impl {
 public:
  Impl() = default;

  explicit Impl(const trait::TraitSet& traitSet) { addTraits(traitSet); }

  Impl(const Impl& other) = default;

  ~Impl() = default;

  [[nodiscard]] trait::TraitSet traitSet() const {
    trait::TraitSet ids;
    ids.reserve(data_.size());
    for (const auto& item : data_) {
      ids.insert(item.first);
    }
    return ids;
  }

  [[nodiscard]] bool hasTrait(const trait::TraitId& traitId) const {
    return static_cast<bool>(data_.count(traitId));
  }

  void addTrait(const trait::TraitId& traitId) { data_[traitId]; }

  void addTraits(const trait::TraitSet& traitSet) {
    for (const auto& traitId : traitSet) {
      data_[traitId];
    }
  }

  // NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
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
    // Use subscript to ensure the trait is added if it is missing
    data_[traitId][propertyKey] = std::move(propertyValue);
  }

  [[nodiscard]] trait::property::KeySet traitPropertyKeys(const trait::TraitId& traitId) const {
    const auto& traitEntry = data_.find(traitId);
    if (traitEntry == data_.end()) {
      return {};
    }
    trait::property::KeySet propertyKeys;
    propertyKeys.reserve(traitEntry->second.size());
    for (const auto& propIter : traitEntry->second) {
      propertyKeys.insert(propIter.first);
    }
    return propertyKeys;
  }

  bool operator==(const Impl& other) const { return data_ == other.data_; }

 private:
  using Properties = std::unordered_map<trait::property::Key, trait::property::Value>;
  using PropertiesByTrait = std::unordered_map<trait::TraitId, Properties>;
  PropertiesByTrait data_;
};

TraitsDataPtr TraitsData::make() { return std::shared_ptr<TraitsData>(new TraitsData()); }

TraitsDataPtr TraitsData::make(const trait::TraitSet& traitSet) {
  return std::shared_ptr<TraitsData>(new TraitsData(traitSet));
}

TraitsDataPtr TraitsData::make(const TraitsDataConstPtr& other) {
  return std::shared_ptr<TraitsData>(new TraitsData(*other));
}

TraitsData::TraitsData() : impl_{std::make_unique<Impl>()} {}

TraitsData::TraitsData(const trait::TraitSet& traitSet)
    : impl_{std::make_unique<Impl>(traitSet)} {}

TraitsData::TraitsData(const TraitsData& other) : impl_{std::make_unique<Impl>(*other.impl_)} {}

TraitsData::~TraitsData() = default;

trait::TraitSet TraitsData::traitSet() const { return impl_->traitSet(); }

void TraitsData::addTrait(const trait::TraitId& traitId) { impl_->addTrait(traitId); }

void TraitsData::addTraits(const trait::TraitSet& traitSet) { impl_->addTraits(traitSet); }

bool TraitsData::hasTrait(const trait::TraitId& traitId) const { return impl_->hasTrait(traitId); }

bool TraitsData::getTraitProperty(trait::property::Value* out, const trait::TraitId& traitId,
                                  const trait::property::Key& propertyKey) const {
  return impl_->getTraitProperty(out, traitId, propertyKey);
}

void TraitsData::setTraitProperty(const trait::TraitId& traitId,
                                  const trait::property::Key& propertyKey,
                                  trait::property::Value propertyValue) {
  impl_->setTraitProperty(traitId, propertyKey, std::move(propertyValue));
}

trait::property::KeySet TraitsData::traitPropertyKeys(const trait::TraitId& traitId) const {
  return impl_->traitPropertyKeys(traitId);
}

bool TraitsData::operator==(const TraitsData& other) const { return *impl_ == *other.impl_; }
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
