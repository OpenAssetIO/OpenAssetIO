// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/managerAPI/ManagerStateBase.hpp>

#include "../_openassetio.hpp"

void registerManagerStateBase(const py::module& mod) {
  using openassetio::managerAPI::ManagerStateBase;
  using openassetio::managerAPI::ManagerStateBasePtr;

  py::class_<ManagerStateBase, ManagerStateBasePtr>(mod, "ManagerStateBase").def(py::init());
}
