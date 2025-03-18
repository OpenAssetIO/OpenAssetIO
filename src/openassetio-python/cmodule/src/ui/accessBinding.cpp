// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/ui/access.hpp>

#include "../_openassetio.hpp"

void registerUIAccess(const py::module& mod) {
  namespace access = openassetio::ui::access;

  py::enum_<access::UIAccess>{mod, "UIAccess"}
      .value("kRead", access::UIAccess::kRead)
      .value("kWrite", access::UIAccess::kWrite)
      .value("kCreateRelated", access::UIAccess::kCreateRelated);
}
