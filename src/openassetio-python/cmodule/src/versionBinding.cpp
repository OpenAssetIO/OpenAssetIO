// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/version.hpp>
#include "_openassetio.hpp"

void registerVersion(py::module& mod) {
  mod.def("majorVersion", &openassetio::majorVersion);
  mod.def("minorVersion", &openassetio::minorVersion);
  mod.def("patchVersion", &openassetio::patchVersion);
  mod.def("versionString", &openassetio::versionString);
}
