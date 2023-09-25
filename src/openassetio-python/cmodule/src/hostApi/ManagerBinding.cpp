// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <algorithm>

#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/errors/BatchElementError.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>

#include "../_openassetio.hpp"

namespace {
using openassetio::EntityReferences;
using openassetio::TraitsDataPtr;
using openassetio::hostApi::Manager;
using openassetio::trait::TraitsDatas;

void validateTraitsDatas(const TraitsDatas& traitsDatas) {
  // Pybind has no built-in way to assert that a collection
  // does not contain any `None` elements, so we must add our
  // own check here.
  if (std::any_of(traitsDatas.begin(), traitsDatas.end(), std::logical_not<TraitsDataPtr>{})) {
    throw openassetio::errors::InputValidationException{"Traits data cannot be None"};
  }
}
}  // namespace

void registerManager(const py::module& mod) {
  namespace access = openassetio::access;
  namespace trait = openassetio::trait;
  using openassetio::ContextConstPtr;
  using openassetio::EntityReference;
  using openassetio::EntityReferences;
  using openassetio::TraitsDataPtr;
  using openassetio::errors::BatchElementError;
  using openassetio::hostApi::Manager;
  using openassetio::hostApi::ManagerPtr;
  using openassetio::managerApi::HostSessionPtr;
  using openassetio::managerApi::ManagerInterfacePtr;

  py::class_<Manager, ManagerPtr> pyManager{mod, "Manager"};

  // BatchElementErrorPolicy tags for tag dispatch overload resolution
  // idiom.
  py::class_<Manager::BatchElementErrorPolicyTag> pyBatchElementErrorPolicyTag{
      pyManager, "BatchElementErrorPolicyTag"};
  // NOLINTNEXTLINE(bugprone-unused-raii)
  py::class_<Manager::BatchElementErrorPolicyTag::Exception>{pyBatchElementErrorPolicyTag,
                                                             "Exception"};
  // NOLINTNEXTLINE(bugprone-unused-raii)
  py::class_<Manager::BatchElementErrorPolicyTag::Variant>{pyBatchElementErrorPolicyTag,
                                                           "Variant"};

  pyBatchElementErrorPolicyTag
      .def_readonly_static("kException", &Manager::BatchElementErrorPolicyTag::kException)
      .def_readonly_static("kVariant", &Manager::BatchElementErrorPolicyTag::kVariant);

  pyManager
      .def(py::init(RetainCommonPyArgs::forFn<&Manager::make>()),
           py::arg("managerInterface").none(false), py::arg("hostSession").none(false))
      .def("identifier", &Manager::identifier)
      .def("displayName", &Manager::displayName)
      .def("info", &Manager::info)
      .def("settings", &Manager::settings)
      .def("initialize", &Manager::initialize, py::arg("managerSettings"))
      .def("flushCaches", &Manager::flushCaches)
      .def("managementPolicy", &Manager::managementPolicy, py::arg("traitSets"),
           py::arg("policyAccess"), py::arg("context").none(false))
      .def("createContext", &Manager::createContext)
      .def("createChildContext", &Manager::createChildContext,
           py::arg("parentContext").none(false))
      .def("persistenceTokenForContext", &Manager::persistenceTokenForContext,
           py::arg("context").none(false))
      .def("contextFromPersistenceToken", &Manager::contextFromPersistenceToken, py::arg("token"))
      .def("isEntityReferenceString", &Manager::isEntityReferenceString, py::arg("someString"))
      .def("createEntityReference", &Manager::createEntityReference,
           py::arg("entityReferenceString"))
      .def("createEntityReferenceIfValid", &Manager::createEntityReferenceIfValid,
           py::arg("entityReferenceString"))
      .def("entityExists", &Manager::entityExists, py::arg("entityReferences"),
           py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))
      .def("updateTerminology", &Manager::updateTerminology, py::arg("terms"))
      .def(
          "resolve",
          py::overload_cast<const EntityReferences&, const trait::TraitSet&, access::ResolveAccess,
                            const ContextConstPtr&, const Manager::ResolveSuccessCallback&,
                            const Manager::BatchElementErrorCallback&>(&Manager::resolve),
          py::arg("entityReferences"), py::arg("traitSet"), py::arg("resolveAccess"),
          py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))
      .def("resolve",
           py::overload_cast<const EntityReference&, const trait::TraitSet&, access::ResolveAccess,
                             const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Exception&>(
               &Manager::resolve),
           py::arg("entityReference"), py::arg("traitSet"), py::arg("resolveAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def("resolve",
           py::overload_cast<const EntityReference&, const trait::TraitSet&, access::ResolveAccess,
                             const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Variant&>(
               &Manager::resolve),
           py::arg("entityReference"), py::arg("traitSet"), py::arg("resolveAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "resolve",
          // TODO(DF): Technically we shouldn't need this overload,
          // since we can use a similar trick to C++ to default the
          // appropriate overload's tag parameter, e.g.
          // `py::arg("errorPolicyTag") = {}`. However, this causes a
          // memory leak in pybind11.
          [](Manager& self, const EntityReference& entityReference,
             const trait::TraitSet& traitSet, const access::ResolveAccess access,
             const ContextConstPtr& context) {
            return self.resolve(entityReference, traitSet, access, context);
          },
          py::arg("entityReference"), py::arg("traitSet"), py::arg("resolveAccess"),
          py::arg("context").none(false))
      .def("resolve",
           py::overload_cast<const EntityReferences&, const trait::TraitSet&,
                             access::ResolveAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Exception&>(
               &Manager::resolve),
           py::arg("entityReferences"), py::arg("traitSet"), py::arg("resolveAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def("resolve",
           py::overload_cast<const EntityReferences&, const trait::TraitSet&,
                             access::ResolveAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Variant&>(
               &Manager::resolve),
           py::arg("entityReferences"), py::arg("traitSet"), py::arg("resolveAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "resolve",
          // TODO(DF): Technically we shouldn't need this overload,
          // since we can use a similar trick to C++ to default the
          // appropriate overload's tag parameter, e.g.
          // `py::arg("errorPolicyTag") = {}`. However, this causes a
          // memory leak in pybind11.
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitSet& traitSet, const access::ResolveAccess resolveAccess,
             const ContextConstPtr& context) {
            return self.resolve(entityReferences, traitSet, resolveAccess, context);
          },
          py::arg("entityReferences"), py::arg("traitSet"), py::arg("resolveAccess"),
          py::arg("context").none(false))
      .def("defaultEntityReference", &Manager::defaultEntityReference, py::arg("traitSets"),
           py::arg("defaultEntityAccess"), py::arg("context").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("getWithRelationship", &Manager::getWithRelationship, py::arg("entityReferences"),
           py::arg("relationshipTraitsData").none(false), py::arg("relationsAccess"),
           py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"),
           py::arg("resultTraitSet") = trait::TraitSet{})
      .def(
          "getWithRelationships",
          [](Manager& self, const EntityReference& entityReference,
             const trait::TraitsDatas& relationshipTraitsDatas,
             const access::RelationsAccess relationsAccess, const ContextConstPtr& context,
             const Manager::RelationshipSuccessCallback& successCallback,
             const Manager::BatchElementErrorCallback& errorCallback,
             const trait::TraitSet& resultTraitSet) {
            validateTraitsDatas(relationshipTraitsDatas);
            self.getWithRelationships(entityReference, relationshipTraitsDatas, relationsAccess,
                                      context, successCallback, errorCallback, resultTraitSet);
          },
          py::arg("entityReference"), py::arg("relationshipTraitsDatas"),
          py::arg("context").none(false), py::arg("context").none(false),
          py::arg("successCallback"), py::arg("errorCallback"),
          py::arg("resultTraitSet") = trait::TraitSet{})
      .def("getWithRelationshipPaged", &Manager::getWithRelationshipPaged,
           py::arg("entityReferences"), py::arg("relationshipTraitsData").none(false),
           py::arg("pageSize"), py::arg("relationsAccess"), py::arg("context").none(false),
           py::arg("successCallback"), py::arg("errorCallback"),
           py::arg("resultTraitSet") = trait::TraitSet{})
      .def(
          "getWithRelationshipsPaged",
          [](Manager& self, const EntityReference& entityReference,
             const trait::TraitsDatas& relationshipTraitsDatas, size_t pageSize,
             const access::RelationsAccess relationsAccess, const ContextConstPtr& context,
             const Manager::PagedRelationshipSuccessCallback& successCallback,
             const Manager::BatchElementErrorCallback& errorCallback,
             const trait::TraitSet& resultTraitSet) {
            validateTraitsDatas(relationshipTraitsDatas);
            self.getWithRelationshipsPaged(entityReference, relationshipTraitsDatas, pageSize,
                                           relationsAccess, context, successCallback,
                                           errorCallback, resultTraitSet);
          },
          py::arg("entityReference"), py::arg("relationshipTraitsDatas"), py::arg("pageSize"),
          py::arg("relationsAccess"), py::arg("context").none(false), py::arg("successCallback"),
          py::arg("errorCallback"), py::arg("resultTraitSet") = trait::TraitSet{})
      .def(
          "preflight",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& traitsHints,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
             const Manager::PreflightSuccessCallback& successCallback,
             const Manager::BatchElementErrorCallback& errorCallback) {
            validateTraitsDatas(traitsHints);
            self.preflight(entityReferences, traitsHints, publishingAccess, context,
                           successCallback, errorCallback);
          },
          py::arg("entityReferences"), py::arg("traitsHints"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))
      .def("preflight",
           py::overload_cast<const EntityReference&, const TraitsDataPtr&,
                             access::PublishingAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Exception&>(
               &Manager::preflight),
           py::arg("entityReference"), py::arg("traitsHint").none(false), py::arg("publishAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def("preflight",
           py::overload_cast<const EntityReference&, const TraitsDataPtr&,
                             access::PublishingAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Variant&>(
               &Manager::preflight),
           py::arg("entityReference"), py::arg("traitsHint").none(false), py::arg("publishAccess"),
           py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "preflight",
          [](Manager& self, const EntityReference& entityReference,
             const TraitsDataPtr& traitsHint, const access::PublishingAccess publishingAccess,
             const ContextConstPtr& context) {
            return self.preflight(entityReference, traitsHint, publishingAccess, context);
          },
          py::arg("entityReference"), py::arg("traitsHint").none(false), py::arg("publishAccess"),
          py::arg("context").none(false))
      .def(
          "preflight",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& traitsHints,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
             const Manager::BatchElementErrorPolicyTag::Exception& tag) {
            validateTraitsDatas(traitsHints);
            return self.preflight(entityReferences, traitsHints, publishingAccess, context, tag);
          },
          py::arg("entityReferences"), py::arg("traitsHints"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "preflight",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& traitsHints,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
             const Manager::BatchElementErrorPolicyTag::Variant& tag) {
            validateTraitsDatas(traitsHints);
            return self.preflight(entityReferences, traitsHints, publishingAccess, context, tag);
          },
          py::arg("entityReferences"), py::arg("traitsHints"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "preflight",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& traitsHints,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context) {
            validateTraitsDatas(traitsHints);
            return self.preflight(entityReferences, traitsHints, publishingAccess, context);
          },
          py::arg("entityReferences"), py::arg("traitsHints"), py::arg("publishAccess"),
          py::arg("context").none(false))
      .def(
          "register",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& entityTraitsDatas,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
             const Manager::RegisterSuccessCallback& successCallback,
             const Manager::BatchElementErrorCallback& errorCallback) {
            validateTraitsDatas(entityTraitsDatas);
            self.register_(entityReferences, entityTraitsDatas, publishingAccess, context,
                           successCallback, errorCallback);
          },
          py::arg("entityReferences"), py::arg("entityTraitsDatas"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))

      .def("register",
           py::overload_cast<const EntityReference&, const TraitsDataPtr&,
                             access::PublishingAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Exception&>(
               &Manager::register_),
           py::arg("entityReference"), py::arg("entityTraitsData").none(false),
           py::arg("publishAccess"), py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def("register",
           py::overload_cast<const EntityReference&, const TraitsDataPtr&,
                             access::PublishingAccess, const ContextConstPtr&,
                             const Manager::BatchElementErrorPolicyTag::Variant&>(
               &Manager::register_),
           py::arg("entityReference"), py::arg("entityTraitsData").none(false),
           py::arg("publishAccess"), py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "register",
          [](Manager& self, const EntityReference& entityReference,
             const TraitsDataPtr& entityTraitsData,
             const access::PublishingAccess publishingAccess, const ContextConstPtr& context) {
            return self.register_(entityReference, entityTraitsData, publishingAccess, context);
          },
          py::arg("entityReference"), py::arg("entityTraitsData").none(false),
          py::arg("publishAccess"), py::arg("context").none(false))
      .def(
          "register",
          [](Manager& self, const EntityReferences& entityReferences,
             const TraitsDatas& entityTraitsDatas, const access::PublishingAccess publishingAccess,
             const ContextConstPtr& context,
             const Manager::BatchElementErrorPolicyTag::Exception& errorPolicyTag) {
            validateTraitsDatas(entityTraitsDatas);
            return self.register_(entityReferences, entityTraitsDatas, publishingAccess, context,
                                  errorPolicyTag);
          },
          py::arg("entityReferences"), py::arg("entityTraitsDatas"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "register",
          [](Manager& self, const EntityReferences& entityReferences,
             const TraitsDatas& entityTraitsDatas, const access::PublishingAccess publishingAccess,
             const ContextConstPtr& context,
             const Manager::BatchElementErrorPolicyTag::Variant& errorPolicyTag) {
            validateTraitsDatas(entityTraitsDatas);
            return self.register_(entityReferences, entityTraitsDatas, publishingAccess, context,
                                  errorPolicyTag);
          },
          py::arg("entityReferences"), py::arg("entityTraitsDatas"), py::arg("publishAccess"),
          py::arg("context").none(false), py::arg("errorPolicyTag"))
      .def(
          "register",
          [](Manager& self, const EntityReferences& entityReferences,
             const TraitsDatas& entityTraitsDatas, const access::PublishingAccess publishingAccess,
             const ContextConstPtr& context) {
            validateTraitsDatas(entityTraitsDatas);
            return self.register_(entityReferences, entityTraitsDatas, publishingAccess, context);
          },
          py::arg("entityReference"), py::arg("entityTraitsData").none(false),
          py::arg("publishAccess"), py::arg("context").none(false));
}
