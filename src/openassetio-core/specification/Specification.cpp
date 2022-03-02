// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/specification/Specification.hpp>
#include <unordered_map>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace specification {

class Specification::Impl {
 public:
  explicit Impl(const TraitIds& traitIds) {
    // Initialise data dict with supported traits.
    for (const auto& traitId : traitIds) {
      data_[traitId];
    }
  }
  ~Impl() = default;

  bool hasTrait(const trait::TraitId& traitId) const {
    return static_cast<bool>(data_.count(traitId));
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

 private:
  using Properties = std::unordered_map<trait::property::Key, trait::property::Value>;
  using PropertiesByTrait = std::unordered_map<trait::TraitId, Properties>;
  PropertiesByTrait data_;
};

Specification::Specification(const TraitIds& traitIds) : impl_{std::make_unique<Impl>(traitIds)} {}

Specification::~Specification() = default;

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
}  // namespace specification
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
