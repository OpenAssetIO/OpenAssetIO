// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/access.hpp>

#include "_openassetio.hpp"

void registerAccess(const py::module& mod) {
  namespace access = openassetio::access;

  py::enum_<access::PolicyAccess>{mod, "PolicyAccess"}
      .value("kRead", access::PolicyAccess::kRead)
      .value("kWrite", access::PolicyAccess::kWrite)
      .value("kCreateRelated", access::PolicyAccess::kCreateRelated);

  py::enum_<access::ResolveAccess>{mod, "ResolveAccess"}
      .value("kRead", access::ResolveAccess::kRead)
      .value("kWrite", access::ResolveAccess::kWrite);

  py::enum_<access::PublishingAccess>{mod, "PublishingAccess"}
      .value("kWrite", access::PublishingAccess::kWrite)
      .value("kCreateRelated", access::PublishingAccess::kCreateRelated);

  py::enum_<access::RelationsAccess>{mod, "RelationsAccess"}
      .value("kRead", access::RelationsAccess::kRead)
      .value("kWrite", access::RelationsAccess::kWrite)
      .value("kCreateRelated", access::RelationsAccess::kCreateRelated);

  py::enum_<access::DefaultEntityAccess>{mod, "DefaultEntityAccess"}
      .value("kRead", access::DefaultEntityAccess::kRead)
      .value("kWrite", access::DefaultEntityAccess::kWrite)
      .value("kCreateRelated", access::DefaultEntityAccess::kCreateRelated);

  mod.attr("kAccessNames") = access::kAccessNames;
}
