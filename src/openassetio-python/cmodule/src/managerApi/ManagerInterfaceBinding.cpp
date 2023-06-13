// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
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

  [[nodiscard]] InfoDictionary info() const override {
    PYBIND11_OVERRIDE(InfoDictionary, ManagerInterface, info, /* no args */);
  }

  [[nodiscard]] InfoDictionary settings(const HostSessionPtr& hostSession) const override {
    PYBIND11_OVERRIDE(InfoDictionary, ManagerInterface, settings, hostSession);
  }

  void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE_PURE(void, ManagerInterface, initialize, std::move(managerSettings),
                           hostSession);
  }

  [[nodiscard]] trait::TraitsDatas managementPolicy(
      const trait::TraitSets& traitSets, const ContextConstPtr& context,
      const HostSessionPtr& hostSession) const override {
    PYBIND11_OVERRIDE_PURE(trait::TraitsDatas, ManagerInterface, managementPolicy, traitSets,
                           context, hostSession);
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
                                             const HostSessionPtr& hostSession) const override {
    PYBIND11_OVERRIDE_PURE(bool, ManagerInterface, isEntityReferenceString, someString,
                           hostSession);
  }

  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               const ContextConstPtr& context, const HostSessionPtr& hostSession,
               const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE_PURE(void, ManagerInterface, resolve, entityReferences, traitSet, context,
                           hostSession, successCallback, errorCallback);
  }

  void getWithRelationship(
      const EntityReferences& entityReferences, const TraitsDataPtr& relationshipTraitsData,
      const trait::TraitSet& resultTraitSet, const ContextConstPtr& context,
      const HostSessionPtr& hostSession,
      const ManagerInterface::RelationshipSuccessCallback& successCallback,
      const ManagerInterface::BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, getWithRelationship, entityReferences,
                      relationshipTraitsData, resultTraitSet, context, hostSession,
                      successCallback, errorCallback);
  }

  void getWithRelationships(
      const EntityReference& entityReference, const trait::TraitsDatas& relationshipTraitsDatas,
      const trait::TraitSet& resultTraitSet, const ContextConstPtr& context,
      const HostSessionPtr& hostSession,
      const ManagerInterface::RelationshipSuccessCallback& successCallback,
      const ManagerInterface::BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE(void, ManagerInterface, getWithRelationships, entityReference,
                      relationshipTraitsDatas, resultTraitSet, context, hostSession,
                      successCallback, errorCallback);
  }

  void preflight(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
                 const ContextConstPtr& context, const HostSessionPtr& hostSession,
                 const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE_PURE(void, ManagerInterface, preflight, entityReferences, traitSet, context,
                           hostSession, successCallback, errorCallback);
  }

  void register_(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsDatas,
                 const ContextConstPtr& context, const HostSessionPtr& hostSession,
                 const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override {
    PYBIND11_OVERRIDE_PURE(void, ManagerInterface, register, entityReferences, traitsDatas,
                           context, hostSession, successCallback, errorCallback);
  }

  // Hoist protected members
  using ManagerInterface::createEntityReference;
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerManagerInterface(const py::module& mod) {
  using openassetio::managerApi::ManagerInterface;
  using openassetio::managerApi::ManagerInterfacePtr;
  using openassetio::managerApi::ManagerStateBasePtr;
  using openassetio::managerApi::PyManagerInterface;

  py::class_<ManagerInterface, PyManagerInterface, ManagerInterfacePtr>(mod, "ManagerInterface")
      .def(py::init())
      .def("identifier", &ManagerInterface::identifier)
      .def("displayName", &ManagerInterface::displayName)
      .def("info", &ManagerInterface::info)
      .def("settings", &ManagerInterface::settings, py::arg("hostSession").none(false))
      .def("initialize", &ManagerInterface::initialize, py::arg("managerSettings"),
           py::arg("hostSession").none(false))
      .def("managementPolicy", &ManagerInterface::managementPolicy, py::arg("traitSets"),
           py::arg("context").none(false), py::arg("hostSession").none(false))
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
      .def("resolve", &ManagerInterface::resolve, py::arg("entityReferences"), py::arg("traitSet"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("getWithRelationship", &ManagerInterface::getWithRelationship,
           py::arg("entityReferences"), py::arg("relationshipTraitsData").none(false),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"), py::arg("resultTraitSet"))
      .def("getWithRelationships", &ManagerInterface::getWithRelationships,
           py::arg("entityReference"), py::arg("relationshipTraitsDatas"),
           py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"), py::arg("resultTraitSet"))
      .def("preflight", &ManagerInterface::preflight, py::arg("entityReferences"),
           py::arg("traitSet"), py::arg("context").none(false), py::arg("hostSession").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("register", &ManagerInterface::register_, py::arg("entityReferences"),
           py::arg("entityTraitsDatas"), py::arg("context").none(false),
           py::arg("hostSession").none(false), py::arg("successCallback"),
           py::arg("errorCallback"))
      .def("_createEntityReference", &PyManagerInterface::createEntityReference,
           py::arg("entityReferenceString"));
}
