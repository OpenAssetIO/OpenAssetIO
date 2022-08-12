// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <pybind11/pybind11.h>

#include <openassetio/BatchElementError.hpp>

#include "_openassetio.hpp"

void registerBatchElementError(const py::module &mod) {
  using openassetio::BatchElementError;

  py::class_<BatchElementError> batchElementError{mod, "BatchElementError", py::is_final()};

  py::enum_<BatchElementError::ErrorCode>{batchElementError, "ErrorCode"}
      .value("kUnknown", BatchElementError::ErrorCode::kUnknown)
      .value("kEntityResolutionError", BatchElementError::ErrorCode::kEntityResolutionError);

  batchElementError
      .def(py::init<BatchElementError::ErrorCode, openassetio::Str>(), py::arg("code"),
           py::arg("message"))
      .def_readonly("code", &BatchElementError::code)
      .def_readonly("message", &BatchElementError::message);
}
