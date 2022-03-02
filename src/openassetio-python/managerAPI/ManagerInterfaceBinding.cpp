// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <openassetio/managerAPI/ManagerInterface.hpp>

#include "../_openassetio.hpp"

void registerManagerInterface(const py::module& mod) {
  using openassetio::managerAPI::ManagerInterface;

  py::class_<ManagerInterface, Holder<ManagerInterface>>(mod, "ManagerInterface").def(py::init());
}
