// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <algorithm>

#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/BatchElementError.hpp>
#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>

#include "../_openassetio.hpp"

void registerManager(const py::module& mod) {
  namespace trait = openassetio::trait;
  using openassetio::ContextConstPtr;
  using openassetio::EntityReference;
  using openassetio::EntityReferences;
  using openassetio::TraitsDataPtr;
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
      .def("managementPolicy", &Manager::managementPolicy, py::arg("traitSets"),
           py::arg("context").none(false))
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
      .def("resolve",
           static_cast<void (Manager::*)(
               const EntityReferences&, const trait::TraitSet&, const ContextConstPtr&,
               const Manager::ResolveSuccessCallback&, const Manager::BatchElementErrorCallback&)>(
               &Manager::resolve),
           py::arg("entityReferences"), py::arg("traitSet"), py::arg("context").none(false),
           py::arg("successCallback"), py::arg("errorCallback"))
      .def("resolve",
           static_cast<TraitsDataPtr (Manager::*)(
               const EntityReference&, const trait::TraitSet&, const ContextConstPtr&,
               const Manager::BatchElementErrorPolicyTag::Exception&)>(&Manager::resolve),
           py::arg("entityReference"), py::arg("traitSet"), py::arg("context").none(false),
           py::arg("errorPolicyTag"))
      .def("resolve",
           static_cast<std::variant<TraitsDataPtr, openassetio::BatchElementError> (Manager::*)(
               const EntityReference&, const trait::TraitSet&, const ContextConstPtr&,
               const Manager::BatchElementErrorPolicyTag::Variant&)>(&Manager::resolve),
           py::arg("entityReference"), py::arg("traitSet"), py::arg("context").none(false),
           py::arg("errorPolicyTag"))
      .def(
          "resolve",
          // TODO(DF): Technically we shouldn't need this overload,
          // since we can use a similar trick to C++ to default the
          // appropriate overload's tag parameter, e.g.
          // `py::arg("errorPolicyTag") = {}`. However, this causes a
          // memory leak in pybind11.
          [](Manager& self, const EntityReference& entityReference,
             const trait::TraitSet& traitSet, const ContextConstPtr& context) {
            return self.resolve(entityReference, traitSet, context);
          },
          py::arg("entityReference"), py::arg("traitSet"), py::arg("context").none(false))
      .def("resolve",
           static_cast<std::vector<TraitsDataPtr> (Manager::*)(
               const EntityReferences&, const trait::TraitSet&, const ContextConstPtr&,
               const Manager::BatchElementErrorPolicyTag::Exception&)>(&Manager::resolve),
           py::arg("entityReferences"), py::arg("traitSet"), py::arg("context").none(false),
           py::arg("errorPolicyTag"))
      .def(
          "resolve",
          static_cast<std::vector<std::variant<TraitsDataPtr, openassetio::BatchElementError>> (
              Manager::*)(const EntityReferences&, const trait::TraitSet&, const ContextConstPtr&,
                          const Manager::BatchElementErrorPolicyTag::Variant&)>(&Manager::resolve),
          py::arg("entityReferences"), py::arg("traitSet"), py::arg("context").none(false),
          py::arg("errorPolicyTag"))
      .def(
          "resolve",
          // TODO(DF): Technically we shouldn't need this overload,
          // since we can use a similar trick to C++ to default the
          // appropriate overload's tag parameter, e.g.
          // `py::arg("errorPolicyTag") = {}`. However, this causes a
          // memory leak in pybind11.
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitSet& traitSet, const ContextConstPtr& context) {
            return self.resolve(entityReferences, traitSet, context);
          },
          py::arg("entityReferences"), py::arg("traitSet"), py::arg("context").none(false))
      .def("preflight", &Manager::preflight, py::arg("entityReferences"), py::arg("traitSet"),
           py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))
      .def(
          "register",
          [](Manager& self, const EntityReferences& entityReferences,
             const trait::TraitsDatas& entityTraitsDatas, const ContextConstPtr& context,
             const Manager::RegisterSuccessCallback& successCallback,
             const Manager::BatchElementErrorCallback& errorCallback) {
            // Pybind has no built-in way to assert that a collection
            // does not contain any `None` elements, so we must add our
            // own check here.
            if (std::any_of(entityTraitsDatas.begin(), entityTraitsDatas.end(),
                            std::logical_not<TraitsDataPtr>{})) {
              throw pybind11::type_error{"Traits data cannot be None"};
            }
            self.register_(entityReferences, entityTraitsDatas, context, successCallback,
                           errorCallback);
          },
          py::arg("entityReferences"), py::arg("entityTraitsDatas"),
          py::arg("context").none(false), py::arg("successCallback"), py::arg("errorCallback"))
      // @todo Remove one C++ API matches Python, and we remove ManagerFactory.py
      .def("_interface", &Manager::_interface)
      .def("_hostSession", &Manager::_hostSession);
}
