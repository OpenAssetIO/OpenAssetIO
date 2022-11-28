// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/log/ConsoleLogger.hpp>

#include "../_openassetio.hpp"

void registerConsoleLogger(const py::module& mod) {
  using openassetio::log::ConsoleLogger;
  using openassetio::log::ConsoleLoggerPtr;
  using openassetio::log::LoggerInterface;

  py::class_<ConsoleLogger, LoggerInterface, ConsoleLoggerPtr>(mod, "ConsoleLogger",
                                                               py::is_final())
      .def(py::init(&ConsoleLogger::make), py::arg("shouldColorOutput") = true);
}
