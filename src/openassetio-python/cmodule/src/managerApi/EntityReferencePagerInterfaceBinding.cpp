// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/functional.h>
#include <pybind11/stl.h>

#include <openassetio/Context.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>
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
struct PyEntityReferencePagerInterface : EntityReferencePagerInterface {
  using EntityReferencePagerInterface::EntityReferencePagerInterface;

  bool hasNext(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE_PURE(bool, EntityReferencePagerInterface, hasNext, hostSession);
  }

  EntityReferencePagerInterface::Page get(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE_PURE(EntityReferencePagerInterface::Page, EntityReferencePagerInterface, get,
                           hostSession);
  }

  void next(const HostSessionPtr& hostSession) override {
    PYBIND11_OVERRIDE_PURE(void, EntityReferencePagerInterface, next, hostSession);
  }
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerEntityReferencePagerInterface(const py::module& mod) {
  using openassetio::managerApi::EntityReferencePagerInterface;
  using openassetio::managerApi::EntityReferencePagerInterfacePtr;
  using openassetio::managerApi::PyEntityReferencePagerInterface;

  py::class_<EntityReferencePagerInterface, PyEntityReferencePagerInterface,
             EntityReferencePagerInterfacePtr>(mod, "EntityReferencePagerInterface")
      .def(py::init())
      .def("hasNext", &EntityReferencePagerInterface::hasNext, py::arg("hostSession").none(false))
      .def("get", &EntityReferencePagerInterface::get, py::arg("hostSession").none(false))
      .def("next", &EntityReferencePagerInterface::next, py::arg("hostSession").none(false));
}
