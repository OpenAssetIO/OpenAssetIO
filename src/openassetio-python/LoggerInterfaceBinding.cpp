// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <openassetio/LoggerInterface.hpp>

#include "_openassetio.hpp"
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
/**
 * Trampoline class required for pybind to bind pure virtual methods
 * and allow C++ -> Python calls via a C++ instance.
 */
struct PyLoggerInterface : LoggerInterface {
  using LoggerInterface::LoggerInterface;

  void log(const Str& message, Severity severity) const override {
    PYBIND11_OVERRIDE_PURE(void, LoggerInterface, log, message, severity);
  }
};
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

void registerLoggerInterface(const py::module& mod) {
  using openassetio::Float;
  using openassetio::LoggerInterface;
  using openassetio::LoggerInterfacePtr;
  using openassetio::PyLoggerInterface;
  using openassetio::Str;

  py::class_<LoggerInterface, PyLoggerInterface, LoggerInterfacePtr> loggerInterface{
      mod, "LoggerInterface"};

  py::enum_<LoggerInterface::Severity>{loggerInterface, "Severity", py::arithmetic()}
      .value("kCritical", LoggerInterface::Severity::kCritical)
      .value("kError", LoggerInterface::Severity::kError)
      .value("kWarning", LoggerInterface::Severity::kWarning)
      .value("kProgress", LoggerInterface::Severity::kProgress)
      .value("kInfo", LoggerInterface::Severity::kInfo)
      .value("kDebug", LoggerInterface::Severity::kDebug)
      .value("kDebugApi", LoggerInterface::Severity::kDebugApi)
      .export_values();

  loggerInterface.def_readonly_static("kSeverityNames", &LoggerInterface::kSeverityNames);

  loggerInterface.def(py::init())
      .def("log", &LoggerInterface::log, py::arg("message"), py::arg("severity"));
}
