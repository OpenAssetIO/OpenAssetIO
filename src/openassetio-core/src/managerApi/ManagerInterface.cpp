// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/TraitsData.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

ManagerInterface::ManagerInterface() = default;

InfoDictionary ManagerInterface::info() { return {}; }

StrMap ManagerInterface::updateTerminology(StrMap terms,
                                           [[maybe_unused]] const HostSessionPtr& hostSession) {
  return terms;
}

InfoDictionary ManagerInterface::settings([[maybe_unused]] const HostSessionPtr& hostSession) {
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
  throw errors::NotImplementedException(
      "createChildState called on a manager that does not implement a custom state.");
}

Str ManagerInterface::persistenceTokenForState(
    [[maybe_unused]] const ManagerStateBasePtr& state,
    [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw errors::NotImplementedException(
      "persistenceTokenForState called on a manager that does not implement a custom state.");
}

ManagerStateBasePtr ManagerInterface::stateFromPersistenceToken(
    [[maybe_unused]] const Str& token, [[maybe_unused]] const HostSessionPtr& hostSession) {
  throw errors::NotImplementedException(
      "stateFromPersistenceToken called on a manager that does not implement a custom state.");
}

// To avoid changing this to non-static in the not too distant, when we
// add manager validation (see https://github.com/OpenAssetIO/OpenAssetIO/issues/553).
// NOLINTNEXTLINE(readability-convert-member-functions-to-static)
EntityReference ManagerInterface::createEntityReference(Str entityReferenceString) const {
  return EntityReference(std::move(entityReferenceString));
}

void ManagerInterface::defaultEntityReference(
    const trait::TraitSets& traitSets,
    [[maybe_unused]] const access::DefaultEntityAccess defaultEntityAccess,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const DefaultEntityReferenceSuccessCallback& successCallback,
    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) {
  const auto size = traitSets.size();
  for (size_t i = 0; i < size; ++i) {
    successCallback(i, {});
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

void ManagerInterface::getWithRelationship(
    const EntityReferences& entityReferences,
    [[maybe_unused]] const trait::TraitsDataPtr& relationshipTraitsData,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet, [[maybe_unused]] size_t pageSize,
    [[maybe_unused]] const access::RelationsAccess relationsAccess,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const RelationshipQuerySuccessCallback& successCallback,
    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) {
  const auto size = entityReferences.size();

  for (std::size_t idx = 0; idx < size; ++idx) {
    successCallback(idx, std::make_shared<EmptyEntityReferencePagerInterface>());
  }
}

void ManagerInterface::getWithRelationships(
    [[maybe_unused]] const EntityReference& entityReference,
    const trait::TraitsDatas& relationshipTraitsDatas,
    [[maybe_unused]] const trait::TraitSet& resultTraitSet, [[maybe_unused]] size_t pageSize,
    [[maybe_unused]] const access::RelationsAccess relationsAccess,
    [[maybe_unused]] const ContextConstPtr& context,
    [[maybe_unused]] const HostSessionPtr& hostSession,
    const RelationshipQuerySuccessCallback& successCallback,
    [[maybe_unused]] const BatchElementErrorCallback& errorCallback) {
  const auto size = relationshipTraitsDatas.size();

  for (std::size_t idx = 0; idx < size; ++idx) {
    successCallback(idx, std::make_shared<EmptyEntityReferencePagerInterface>());
  }
}

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
