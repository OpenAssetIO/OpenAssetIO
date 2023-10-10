// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/typedefs.hpp>

#include "../_openassetio.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyManagerInterface : ManagerInterface {
  using ManagerInterface::ManagerInterface;

  using PyRetainingManagerStateBasePtr = PyRetainingSharedPtr<ManagerStateBase>;

  [[nodiscard]] Identifier identifier() const override {
    PYBIND11_OVERRIDE_PURE(Identifier, ManagerInterface, identifier, /* no args */);
  }

  [[nodiscard]] Str displayName() const override {
    PYBIND11_OVERRIDE_PURE(Str, ManagerInterface, displayName, /* no args */);
  }

  [[nodiscard]] InfoDictionary info() override {
    PYBIND11_OVERRIDE(InfoDictionary, ManagerInterface, info, /* no args */);
  }

  [[nodiscard]] InfoDictionary settings(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(InfoDictionary, ManagerInterface, settings, hostSession);
  }

  void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, initialize, std::move(managerSettings), hostSession);
  }

  void flushCaches(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, flushCaches, hostSession);
  }

  [[nodiscard]] trait::TraitsDatas managementPolicy(const trait::TraitSets& traitSets,
                                                    access::PolicyAccess policyAccess,
                                                    const ContextConstPtr& context,
                                                    const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(trait::TraitsDatas, ManagerInterface, managementPolicy, traitSets,
                      policyAccess, context, hostSession);
  }

  ManagerStateBasePtr createState(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(PyRetainingManagerStateBasePtr, ManagerInterface, createState, hostSession);
  }

  ManagerStateBasePtr createChildState(const ManagerStateBasePtr& parentState,
                                       const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(PyRetainingManagerStateBasePtr, ManagerInterface, createChildState,
                      parentState, hostSession);
  }

  Str persistenceTokenForState(const ManagerStateBasePtr& parentState,
                               const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(Str, ManagerInterface, persistenceTokenForState, parentState, hostSession);
  }

  ManagerStateBasePtr stateFromPersistenceToken(const Str& token,
                                                const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(PyRetainingManagerStateBasePtr, ManagerInterface, stateFromPersistenceToken,
                      token, hostSession);
  }

  [[nodiscard]] bool isEntityReferenceString(const Str& someString,
                                             const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(bool, ManagerInterface, isEntityReferenceString, someString, hostSession);
  }

  void entityExists(const EntityReferences& entityReferences, const ContextConstPtr& context,
                    const HostSessionPtr& hostSession,
                    const ExistsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, entityExists, entityReferences, context, hostSession,
                      successCallback, errorCallback);
  }

  [[nodiscard]] bool hasCapability(ManagerInterface::Capability capability) override {
    PYBIND11_OVERRIDE_PURE(bool, ManagerInterface, hasCapability, capability);
  }

  [[nodiscard]] StrMap updateTerminology(StrMap terms,
                                         const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE(StrMap, ManagerInterface, updateTerminology, std::move(terms), hostSession);
  }

  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               const access::ResolveAccess resolveAccess, const ContextConstPtr& context,
               const HostSessionPtr& hostSession, const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, resolve, entityReferences, traitSet, resolveAccess,
                      context, hostSession, successCallback, errorCallback);
  }

  void defaultEntityReference(const trait::TraitSets& traitSets,
                              const access::DefaultEntityAccess defaultEntityAccess,
                              const ContextConstPtr& context, const HostSessionPtr& hostSession,
                              const DefaultEntityReferenceSuccessCallback& successCallback,
                              const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, defaultEntityReference, traitSets,
                      defaultEntityAccess, context, hostSession, successCallback, errorCallback);
  }

  void getWithRelationship(
      const EntityReferences& entityReferences, const trait::TraitsDataPtr& relationshipTraitsData,
      const trait::TraitSet& resultTraitSet, size_t pageSize,
      const access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const HostSessionPtr& hostSession,
      const ManagerInterface::RelationshipQuerySuccessCallback& successCallback,
      const ManagerInterface::BatchElementErrorCallback& errorCallback) override {
    OPENASSETIO_PYBIND11_OVERRIDE_ARGS(
        void, ManagerInterface, getWithRelationship,
        (entityReferences, relationshipTraitsData, resultTraitSet, pageSize, relationsAccess,
         context, hostSession, successCallback, errorCallback),
        entityReferences, relationshipTraitsData, resultTraitSet, pageSize, relationsAccess,
        context, hostSession, RetainCommonPyArgs::forFn(successCallback), errorCallback);
  }

  void getWithRelationships(
      const EntityReference& entityReference, const trait::TraitsDatas& relationshipTraitsDatas,
      const trait::TraitSet& resultTraitSet, size_t pageSize,
      const access::RelationsAccess relationsAccess, const ContextConstPtr& context,
      const HostSessionPtr& hostSession,
      const ManagerInterface::RelationshipQuerySuccessCallback& successCallback,
      const ManagerInterface::BatchElementErrorCallback& errorCallback) override {
    OPENASSETIO_PYBIND11_OVERRIDE_ARGS(
        void, ManagerInterface, getWithRelationships,
        (entityReference, relationshipTraitsDatas, resultTraitSet, pageSize, relationsAccess,
         context, hostSession, successCallback, errorCallback),
        entityReference, relationshipTraitsDatas, resultTraitSet, pageSize, relationsAccess,
        context, hostSession, RetainCommonPyArgs::forFn(successCallback), errorCallback);
  }

  void preflight(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsHints,
                 const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const HostSessionPtr& hostSession,
                 const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, preflight, entityReferences, traitsHints,
                      publishingAccess, context, hostSession, successCallback, errorCallback);
  }

  void register_(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsDatas,
                 const access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const HostSessionPtr& hostSession, const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE_NAME(void, ManagerInterface, "register", register_, entityReferences,
                           traitsDatas, publishingAccess, context, hostSession, successCallback,
                           errorCallback);
  }

  // Hoist protected members
  using ManagerInterface::createEntityReference;
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerManagerInterface(const py::module& mod) {
  using openassetio::ContextConstPtr;
  using openassetio::EntityReference;
  using openassetio::EntityReferences;
  using openassetio::managerApi::HostSessionPtr;
  using openassetio::managerApi::ManagerInterface;
  using openassetio::managerApi::ManagerInterfacePtr;
  using openassetio::managerApi::ManagerStateBasePtr;
  using openassetio::managerApi::PyManagerInterface;
  using openassetio::trait::TraitsDataPtr;

  py::class_<ManagerInterface, PyManagerInterface, ManagerInterfacePtr> pyManagerInterface(
      mod, "ManagerInterface");

  py::enum_<ManagerInterface::Capability>{pyManagerInterface, "Capability"}
      .value("kEntityReferenceIdentification",
             ManagerInterface::Capability::kEntityReferenceIdentification)
      .value("kManagementPolicyQueries", ManagerInterface::Capability::kManagementPolicyQueries)
      .value("kStatefulContexts", ManagerInterface::Capability::kStatefulContexts)
      .value("kCustomTerminology", ManagerInterface::Capability::kCustomTerminology)
      .value("kResolution", ManagerInterface::Capability::kResolution)
      .value("kPublishing", ManagerInterface::Capability::kPublishing)
      .value("kRelationshipQueries", ManagerInterface::Capability::kRelationshipQueries)
      .value("kExistenceQueries", ManagerInterface::Capability::kExistenceQueries)
      .value("kDefaultEntityReferences", ManagerInterface::Capability::kDefaultEntityReferences);

  pyManagerInterface.attr("kCapabilityNames") = ManagerInterface::kCapabilityNames;

  pyManagerInterface.def(py::init())
      .def("identifier", &ManagerInterface::identifier)
      .def("displayName", &ManagerInterface::displayName)
      .def("info", &ManagerInterface::info)
      .def("settings", &ManagerInterface::settings, py::arg("hostSession").none(false))
      .def("initialize", &ManagerInterface::initialize, py::arg("managerSettings"),
           py::arg("hostSession").none(false))
      .def("flushCaches", &ManagerInterface::flushCaches, py::arg("hostSession").none(false))
      .def("managementPolicy", &ManagerInterface::managementPolicy, py::arg("traitSets"),
           py::arg("access"), py::arg("context").none(false), py::arg("hostSession").none(false))
      .def("createState", &ManagerInterface::createState, py::arg("hostSession").none(false))
      .def("createChildState", RetainCommonPyArgs::forFn<&ManagerInterface::createChildState>(),
           py::arg("parentState").none(false), py::arg("hostSession").none(false))
      .def("persistenceTokenForState",
           RetainCommonPyArgs::forFn<&ManagerInterface::persistenceTokenForState>(),
           py::arg("state").none(false), py::arg("hostSession").none(false))
      .def("stateFromPersistenceToken", &ManagerInterface::stateFromPersistenceToken,
           py::arg("token"), py::arg("hostSession").none(false))
      .def("isEntityReferenceString", &ManagerInterface::isEntityReferenceString,
           py::arg("someString"), py::arg("hostSession").none(false))
      .def("entityExists", &ManagerInterface::entityExists, py::arg("entityReferences"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("hasCapability", &ManagerInterface::hasCapability, py::arg("capability"))
      .def("updateTerminology", &ManagerInterface::updateTerminology, py::arg("terms"),
           py::arg("hostSession").none(false))
      .def("resolve", &ManagerInterface::resolve, py::arg("entityReferences"), py::arg("traitSet"),
           py::arg("access"), py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("defaultEntityReference", &ManagerInterface::defaultEntityReference,
           py::arg("traitSets"), py::arg("defaultEntityAccess"), py::arg("context").none(false),
           py::arg("hostSession").none(false), py::arg("successCallback"),
           py::arg("errorCallback"))
      .def("getWithRelationship", &ManagerInterface::getWithRelationship,
           py::arg("entityReferences"), py::arg("relationshipTraitsData").none(false),
           py::arg("resultTraitSet"), py::arg("pageSize"), py::arg("relationsAccess"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("getWithRelationships", &ManagerInterface::getWithRelationships,
           py::arg("entityReference"), py::arg("relationshipTraitsDatas"),
           py::arg("resultTraitSet"), py::arg("pageSize"), py::arg("relationsAccess"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("preflight", &ManagerInterface::preflight, py::arg("entityReferences"),
           py::arg("traitsHints"), py::arg("publishingAccess"), py::arg("context").none(false),
           py::arg("hostSession").none(false), py::arg("successCallback"),
           py::arg("errorCallback"))
      .def("register", &ManagerInterface::register_, py::arg("entityReferences"),
           py::arg("entityTraitsDatas"), py::arg("publishingAccess"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("_createEntityReference", &PyManagerInterface::createEntityReference,
           py::arg("entityReferenceString"));
}
