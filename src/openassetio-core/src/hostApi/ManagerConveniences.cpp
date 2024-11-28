// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <cstddef>
#include <optional>
#include <stdexcept>
#include <utility>
#include <variant>
#include <vector>

#include <fmt/format.h>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/access.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/internal.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

#include "../errors/exceptionMessages.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

namespace {
template <class Container>
decltype(auto) safeGet(Container &container, const std::size_t idx) {
  try {
    return container.at(idx);
  } catch (const std::out_of_range &) {
    throw errors::InputValidationException(
        fmt::format("Index '{}' out of bounds for batch size of {}", idx, container.size()));
  }
}

template <class Container, class Element>
void safeSet(Container &container, const std::size_t idx, Element &&element) {
  safeGet(container, idx) = std::forward<Element>(element);
}
}  // namespace

// The definitions below are the "convenience" method signatures -
// alternate, often friendlier signatures wrapping the core batch-first
// callback-based member functions found in `Manager.cpp`

trait::TraitsDataPtr Manager::managementPolicy(const trait::TraitSet &traitSet,
                                               access::PolicyAccess policyAccess,
                                               const ContextConstPtr &context) {
  return managementPolicy(trait::TraitSets{traitSet}, policyAccess, context).at(0);
}

/******************************************
 * defaultEntityReference
 ******************************************/

// Singular Except
std::optional<EntityReference> Manager::defaultEntityReference(
    const trait::TraitSet &traitSet, access::DefaultEntityAccess defaultEntityAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::optional<EntityReference> result;
  defaultEntityReference(
      {traitSet}, defaultEntityAccess, context,
      [&result]([[maybe_unused]] std::size_t index,
                std::optional<EntityReference> entityReference) {
        result = std::move(entityReference);
      },
      [&traitSet, defaultEntityAccess](const std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(defaultEntityAccess), std::nullopt,
            traitSet);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Singular variant
std::variant<errors::BatchElementError, std::optional<EntityReference>>
Manager::defaultEntityReference(
    const trait::TraitSet &traitSet, access::DefaultEntityAccess defaultEntityAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, std::optional<EntityReference>> result;
  defaultEntityReference(
      {traitSet}, defaultEntityAccess, context,
      [&result]([[maybe_unused]] std::size_t index,
                std::optional<EntityReference> entityReference) {
        result = std::move(entityReference);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<std::optional<EntityReference>> Manager::defaultEntityReference(
    const trait::TraitSets &traitSets, access::DefaultEntityAccess defaultEntityAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<std::optional<EntityReference>> results;
  results.resize(traitSets.size());

  defaultEntityReference(
      traitSets, defaultEntityAccess, context,
      [&results](std::size_t index, std::optional<EntityReference> entityReference) {
        safeSet(results, index, std::move(entityReference));
      },
      [&traitSets, defaultEntityAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(defaultEntityAccess), std::nullopt,
            safeGet(traitSets, index));
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return results;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, std::optional<EntityReference>>>
Manager::defaultEntityReference(
    const trait::TraitSets &traitSets, access::DefaultEntityAccess defaultEntityAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, std::optional<EntityReference>>> results;
  results.resize(traitSets.size());
  defaultEntityReference(
      traitSets, defaultEntityAccess, context,
      [&results](std::size_t index, std::optional<EntityReference> entityReference) {
        safeSet(results, index, std::move(entityReference));
      },
      [&results](std::size_t index, errors::BatchElementError error) {
        safeSet(results, index, std::move(error));
      });

  return results;
}

/******************************************
 * entityExists
 ******************************************/

// Singular Except
bool Manager::entityExists(
    const EntityReference &entityReference, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  bool result{};
  entityExists(
      {entityReference}, context,
      [&result]([[maybe_unused]] std::size_t index, bool exists) { result = exists; },
      [&entityReference](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(error, index, std::nullopt,
                                                              entityReference, std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Singular variant
std::variant<errors::BatchElementError, bool> Manager::entityExists(
    const EntityReference &entityReference, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, bool> result;
  entityExists(
      {entityReference}, context,
      [&result]([[maybe_unused]] std::size_t index, bool exists) { result = exists; },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<Manager::BoolAsUint> Manager::entityExists(
    const EntityReferences &entityReferences, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<BoolAsUint> results;
  results.resize(entityReferences.size());

  entityExists(
      entityReferences, context,
      [&results](std::size_t index, bool exists) {
        safeSet(results, index, static_cast<BoolAsUint>(exists));
      },
      [&entityReferences](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, std::nullopt, safeGet(entityReferences, index), std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return results;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, bool>> Manager::entityExists(
    const EntityReferences &entityReferences, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, bool>> results;
  results.resize(entityReferences.size());
  entityExists(
      entityReferences, context,
      [&results](std::size_t index, bool exists) { safeSet(results, index, exists); },
      [&results](std::size_t index, errors::BatchElementError error) {
        safeSet(results, index, std::move(error));
      });
  return results;
}

/******************************************
 * entityTraits
 ******************************************/

// Singular Except
trait::TraitSet Manager::entityTraits(
    const EntityReference &entityReference, const access::EntityTraitsAccess entityTraitsAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  trait::TraitSet result;
  entityTraits(
      {entityReference}, entityTraitsAccess, context,
      [&result]([[maybe_unused]] std::size_t index, trait::TraitSet traitSet) {
        result = std::move(traitSet);
      },
      [&entityReference, entityTraitsAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(entityTraitsAccess),
            entityReference, std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Singular variant
std::variant<errors::BatchElementError, trait::TraitSet> Manager::entityTraits(
    const EntityReference &entityReference, const access::EntityTraitsAccess entityTraitsAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, trait::TraitSet> result;
  entityTraits(
      {entityReference}, entityTraitsAccess, context,
      [&result]([[maybe_unused]] std::size_t index, trait::TraitSet traitSet) {
        result = std::move(traitSet);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<trait::TraitSet> Manager::entityTraits(
    const EntityReferences &entityReferences, const access::EntityTraitsAccess entityTraitsAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<trait::TraitSet> results;
  results.resize(entityReferences.size());

  entityTraits(
      entityReferences, entityTraitsAccess, context,
      [&results](std::size_t index, trait::TraitSet traitSet) {
        safeSet(results, index, std::move(traitSet));
      },
      [&entityReferences, entityTraitsAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(entityTraitsAccess),
            safeGet(entityReferences, index), std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return results;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, trait::TraitSet>> Manager::entityTraits(
    const EntityReferences &entityReferences, const access::EntityTraitsAccess entityTraitsAccess,
    const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, trait::TraitSet>> results;
  results.resize(entityReferences.size());
  entityTraits(
      entityReferences, entityTraitsAccess, context,
      [&results](std::size_t index, trait::TraitSet traitSet) {
        safeSet(results, index, std::move(traitSet));
      },
      [&results](std::size_t index, errors::BatchElementError error) {
        safeSet(results, index, std::move(error));
      });
  return results;
}

/******************************************
 * resolve
 ******************************************/

// Singular Except
trait::TraitsDataPtr Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  trait::TraitsDataPtr resolveResult;
  resolve(
      {entityReference}, traitSet, resolveAccess, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, trait::TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [&entityReference, resolveAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(resolveAccess), entityReference,
            std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return resolveResult;
}

// Singular variant
std::variant<errors::BatchElementError, trait::TraitsDataPtr> Manager::resolve(
    const EntityReference &entityReference, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, trait::TraitsDataPtr> resolveResult;
  resolve(
      {entityReference}, traitSet, resolveAccess, context,
      [&resolveResult]([[maybe_unused]] std::size_t index, trait::TraitsDataPtr data) {
        resolveResult = std::move(data);
      },
      [&resolveResult]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        resolveResult = std::move(error);
      });

  return resolveResult;
}

// Multi except
std::vector<trait::TraitsDataPtr> Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<trait::TraitsDataPtr> resolveResult;
  resolveResult.resize(entityReferences.size());

  resolve(
      entityReferences, traitSet, resolveAccess, context,
      [&resolveResult](std::size_t index, trait::TraitsDataPtr data) {
        safeSet(resolveResult, index, std::move(data));
      },
      [&entityReferences, resolveAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(resolveAccess),
            safeGet(entityReferences, index), std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return resolveResult;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, trait::TraitsDataPtr>> Manager::resolve(
    const EntityReferences &entityReferences, const trait::TraitSet &traitSet,
    const access::ResolveAccess resolveAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, trait::TraitsDataPtr>> resolveResult;
  resolveResult.resize(entityReferences.size());
  resolve(
      entityReferences, traitSet, resolveAccess, context,
      [&resolveResult](std::size_t index, trait::TraitsDataPtr data) {
        safeSet(resolveResult, index, std::move(data));
      },
      [&resolveResult](std::size_t index, errors::BatchElementError error) {
        safeSet(resolveResult, index, std::move(error));
      });

  return resolveResult;
}

/******************************************
 * preflight
 ******************************************/

EntityReference Manager::preflight(
    const EntityReference &entityReference, const trait::TraitsDataPtr &traitsHint,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result{""};
  preflight(
      {entityReference}, {traitsHint}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [&entityReference, publishingAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(publishingAccess), entityReference,
            std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

std::variant<errors::BatchElementError, EntityReference> Manager::preflight(
    const EntityReference &entityReference, const trait::TraitsDataPtr &traitsHint,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, EntityReference> result;
  preflight(
      {entityReference}, {traitsHint}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference preflightedRef) {
        result = std::move(preflightedRef);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

EntityReferences Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReferences results;
  results.resize(entityReferences.size(), EntityReference{""});

  preflight(
      entityReferences, traitsHints, publishingAccess, context,
      [&results](std::size_t index, EntityReference preflightedRef) {
        safeSet(results, index, std::move(preflightedRef));
      },
      [&entityReferences, publishingAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(publishingAccess),
            safeGet(entityReferences, index), std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return results;
}

std::vector<std::variant<errors::BatchElementError, EntityReference>> Manager::preflight(
    const EntityReferences &entityReferences, const trait::TraitsDatas &traitsHints,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const Manager::BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReference>> results;
  results.resize(entityReferences.size());
  preflight(
      entityReferences, traitsHints, publishingAccess, context,
      [&results](std::size_t index, EntityReference entityReference) {
        safeSet(results, index, std::move(entityReference));
      },
      [&results](std::size_t index, errors::BatchElementError error) {
        safeSet(results, index, std::move(error));
      });

  return results;
}

/******************************************
 * register_
 ******************************************/

// Singular Except
EntityReference Manager::register_(
    const EntityReference &entityReference, const trait::TraitsDataPtr &entityTraitsData,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReference result("");
  register_(
      {entityReference}, {entityTraitsData}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [&entityReference, publishingAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(publishingAccess), entityReference,
            std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Singular variant
std::variant<errors::BatchElementError, EntityReference> Manager::register_(
    const EntityReference &entityReference, const trait::TraitsDataPtr &entityTraitsData,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, EntityReference> result;
  register_(
      {entityReference}, {entityTraitsData}, publishingAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReference registeredRef) {
        result = std::move(registeredRef);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      });

  return result;
}

// Multi except
std::vector<EntityReference> Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<EntityReference> result;
  result.resize(entityReferences.size(), EntityReference{""});

  register_(
      entityReferences, entityTraitsDatas, publishingAccess, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        safeSet(result, index, std::move(registeredRef));
      },
      [&entityReferences, publishingAccess](std::size_t index, errors::BatchElementError error) {
        // Implemented as if FAILFAST is true.
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(publishingAccess),
            safeGet(entityReferences, index), std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      });

  return result;
}

// Multi variant
std::vector<std::variant<errors::BatchElementError, EntityReference>> Manager::register_(
    const EntityReferences &entityReferences, const trait::TraitsDatas &entityTraitsDatas,
    const access::PublishingAccess publishingAccess, const ContextConstPtr &context,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReference>> result;
  result.resize(entityReferences.size());
  register_(
      entityReferences, entityTraitsDatas, publishingAccess, context,
      [&result](std::size_t index, EntityReference registeredRef) {
        safeSet(result, index, std::move(registeredRef));
      },
      [&result](std::size_t index, errors::BatchElementError error) {
        safeSet(result, index, std::move(error));
      });

  return result;
}

/******************************************
 * getWithRelationship
 ******************************************/

// Singular Except
EntityReferencePagerPtr Manager::getWithRelationship(
    const EntityReference &entityReference, const trait::TraitsDataPtr &relationshipTraitsData,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  EntityReferencePagerPtr result = nullptr;
  getWithRelationship(
      {entityReference}, relationshipTraitsData, pageSize, relationsAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReferencePagerPtr pager) {
        result = std::move(pager);
      },
      [&entityReference, relationsAccess](std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(relationsAccess), entityReference,
            std::nullopt);
        throw errors::BatchElementException(index, std::move(error), msg);
      },
      resultTraitSet);

  return result;
}

// Singular Variant
std::variant<errors::BatchElementError, EntityReferencePagerPtr> Manager::getWithRelationship(
    const EntityReference &entityReference, const trait::TraitsDataPtr &relationshipTraitsData,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::variant<errors::BatchElementError, EntityReferencePagerPtr> result;
  getWithRelationship(
      {entityReference}, relationshipTraitsData, pageSize, relationsAccess, context,
      [&result]([[maybe_unused]] std::size_t index, EntityReferencePagerPtr pager) {
        result = std::move(pager);
      },
      [&result]([[maybe_unused]] std::size_t index, errors::BatchElementError error) {
        result = std::move(error);
      },
      resultTraitSet);

  return result;
}

// Multi Except
std::vector<EntityReferencePagerPtr> Manager::getWithRelationship(
    const EntityReferences &entityReferences, const trait::TraitsDataPtr &relationshipTraitsData,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<EntityReferencePagerPtr> result;
  result.resize(entityReferences.size());

  getWithRelationship(
      entityReferences, relationshipTraitsData, pageSize, relationsAccess, context,
      [&result](std::size_t index, EntityReferencePagerPtr pager) {
        safeSet(result, index, std::move(pager));
      },
      [&entityReferences, &relationshipTraitsData, relationsAccess](
          std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(relationsAccess),
            safeGet(entityReferences, index), relationshipTraitsData->traitSet());
        throw errors::BatchElementException(index, std::move(error), msg);
      },
      resultTraitSet);

  return result;
}

// Multi Variant
std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>>
Manager::getWithRelationship(
    const EntityReferences &entityReferences, const trait::TraitsDataPtr &relationshipTraitsData,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>> result;
  result.resize(entityReferences.size());

  getWithRelationship(
      entityReferences, relationshipTraitsData, pageSize, relationsAccess, context,
      [&result](std::size_t index, EntityReferencePagerPtr pager) {
        safeSet(result, index, std::move(pager));
      },
      [&result](std::size_t index, errors::BatchElementError error) {
        safeSet(result, index, std::move(error));
      },
      resultTraitSet);
  return result;
}

/******************************************
 * getWithRelationships. No singulars as they mirror GetWithRelationship
 ******************************************/

// Multi Except
std::vector<EntityReferencePagerPtr> Manager::getWithRelationships(
    const EntityReference &entityReference, const trait::TraitsDatas &relationshipTraitsDatas,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Exception &errorPolicyTag) {
  std::vector<EntityReferencePagerPtr> result;
  result.resize(relationshipTraitsDatas.size(), nullptr);
  getWithRelationships(
      entityReference, relationshipTraitsDatas, pageSize, relationsAccess, context,
      [&result](std::size_t index, EntityReferencePagerPtr pager) {
        safeSet(result, index, std::move(pager));
      },
      [&entityReference, &relationshipTraitsDatas, relationsAccess](
          std::size_t index, errors::BatchElementError error) {
        auto msg = errors::createBatchElementExceptionMessage(
            error, index, static_cast<internal::access::Access>(relationsAccess), entityReference,
            safeGet(relationshipTraitsDatas, index)->traitSet());
        throw errors::BatchElementException(index, std::move(error), msg);
      },
      resultTraitSet);

  return result;
}

// Multi Variant
std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>>
Manager::getWithRelationships(
    const EntityReference &entityReference, const trait::TraitsDatas &relationshipTraitsDatas,
    const size_t pageSize, const access::RelationsAccess relationsAccess,
    const ContextConstPtr &context, const trait::TraitSet &resultTraitSet,
    [[maybe_unused]] const BatchElementErrorPolicyTag::Variant &errorPolicyTag) {
  std::vector<std::variant<errors::BatchElementError, EntityReferencePagerPtr>> result;
  result.resize(relationshipTraitsDatas.size());
  getWithRelationships(
      entityReference, relationshipTraitsDatas, pageSize, relationsAccess, context,
      [&result](std::size_t index, EntityReferencePagerPtr pager) {
        safeSet(result, index, std::move(pager));
      },
      [&result](std::size_t index, errors::BatchElementError error) {
        safeSet(result, index, std::move(error));
      },
      resultTraitSet);

  return result;
}

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
