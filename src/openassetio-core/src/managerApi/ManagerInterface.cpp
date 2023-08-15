// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

ManagerInterface::ManagerInterface() = default;

InfoDictionary ManagerInterface::info() const { return {}; }

StrMap ManagerInterface::updateTerminology(
    StrMap terms, [[maybe_unused]] const HostSessionPtr& hostSession) const {
  return terms;
}

InfoDictionary ManagerInterface::settings(
    [[maybe_unused]] const HostSessionPtr& hostSession) const {
  return openassetio::InfoDictionary{};
}

void ManagerInterface::flushCaches([[maybe_unused]] const HostSessionPtr& hostSession) {}

ManagerStateBasePtr ManagerInterface::createState(
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  return nullptr;
}

ManagerStateBasePtr ManagerInterface::createChildState(
    [[maybe_unused]] const ManagerStateBasePtr& parentState,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "createChildState called on a manager that does not implement a custom state.");
}

Str ManagerInterface::persistenceTokenForState(
    [[maybe_unused]] const ManagerStateBasePtr& state,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "persistenceTokenForState called on a manager that does not implement a custom state.");
}

ManagerStateBasePtr ManagerInterface::stateFromPersistenceToken(
    [[maybe_unused]] const Str& token, [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw std::runtime_error(
      "stateFromPersistenceToken called on a manager that does not implement a custom state.");
}

// To avoid changing this to non-static in the not too distant, when we
// add manager validation (see https://github.com/OpenAssetIO/OpenAssetIO/issues/553).
// NOLINTNEXTLINE(readability-convert-member-functions-to-static)
EntityReference ManagerInterface::createEntityReference(Str entityReferenceString) const {
  return EntityReference(std::move(entityReferenceString));
}

void ManagerInterface::getWithRelationship(
    const EntityReferences& entityReferences,
    [[maybe_unused]] const TraitsDataPtr& relationshipTraitsData,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const ManagerInterface::RelationshipSuccessCallback& successCallback,
    [[maybe_unused]] const ManagerInterface::BatchElementErrorCallback& errorCallback) {
  for (EntityReferences::size_type idx = 0, size = entityReferences.size(); idx < size; ++idx) {
    successCallback(idx, {});
  }
}
void ManagerInterface::getWithRelationships(
    [[maybe_unused]] const EntityReference& entityReference,
    const trait::TraitsDatas& relationshipTraitsDatas,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const ManagerInterface::RelationshipSuccessCallback& successCallback,
    [[maybe_unused]] const ManagerInterface::BatchElementErrorCallback& errorCallback) {
  for (trait::TraitsDatas::size_type idx = 0, size = relationshipTraitsDatas.size(); idx < size;
       ++idx) {
    successCallback(idx, {});
  }
}

namespace {
/*
 * A dummy pager interface that acts as if it has no data. For use in
 * getWithRelationship[s] default implementation.
 */
class EmptyEntityReferencePagerInterface : public managerApi::EntityReferencePagerInterface {
  bool hasNext([[maybe_unused]] const HostSessionPtr& hsp) override { return false; }

  Page get([[maybe_unused]] const HostSessionPtr& hsp) override { return {}; }

  void next([[maybe_unused]] const HostSessionPtr& hsp) override {}
};

}  // namespace

void ManagerInterface::getWithRelationshipPaged(
    const EntityReferences& entityReferences,
    [[maybe_unused]] const TraitsDataPtr& relationshipTraitsData,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet, [[maybe_unused]] size_t pageSize,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const PagedRelationshipSuccessCallback& successCallback,
    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) {
  const auto size = entityReferences.size();

  for (std::size_t idx = 0; idx < size; ++idx) {
    successCallback(idx, std::make_shared<EmptyEntityReferencePagerInterface>());
  }
}

void ManagerInterface::getWithRelationshipsPaged(
    [[maybe_unused]] const EntityReference& entityReference,
    const trait::TraitsDatas& relationshipTraitsDatas,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet, [[maybe_unused]] size_t pageSize,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const PagedRelationshipSuccessCallback& successCallback,
    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) {
  const auto size = relationshipTraitsDatas.size();

  for (std::size_t idx = 0; idx < size; ++idx) {
    successCallback(idx, std::make_shared<EmptyEntityReferencePagerInterface>());
  }
}

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
