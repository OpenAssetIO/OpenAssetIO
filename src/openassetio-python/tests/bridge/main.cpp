// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#define CATCH_CONFIG_RUNNER
#include <pybind11/embed.h>
#include <catch2/catch.hpp>

namespace py = pybind11;

int main(int argc, char* argv[]) {
  py::scoped_interpreter guard{};
  return Catch::Session().run(argc, argv);
}
