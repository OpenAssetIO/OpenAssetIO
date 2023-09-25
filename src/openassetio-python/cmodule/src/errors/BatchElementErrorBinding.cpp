// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/errors/BatchElementError.hpp>

#include "../_openassetio.hpp"

void registerBatchElementError(const py::module &mod) {
  using openassetio::errors::BatchElementError;

  py::class_<BatchElementError> batchElementError{mod, "BatchElementError", py::is_final()};

  py::enum_<BatchElementError::ErrorCode>{batchElementError, "ErrorCode"}
      .value("kUnknown", BatchElementError::ErrorCode::kUnknown)
      .value("kInvalidEntityReference", BatchElementError::ErrorCode::kInvalidEntityReference)
      .value("kMalformedEntityReference", BatchElementError::ErrorCode::kMalformedEntityReference)
      .value("kEntityAccessError", BatchElementError::ErrorCode::kEntityAccessError)
      .value("kEntityResolutionError", BatchElementError::ErrorCode::kEntityResolutionError)
      .value("kInvalidPreflightHint", BatchElementError::ErrorCode::kInvalidPreflightHint)
      .value("kInvalidTraitSet", BatchElementError::ErrorCode::kInvalidTraitSet);

  batchElementError
      .def(py::init<BatchElementError::ErrorCode, openassetio::Str>(), py::arg("code"),
           py::arg("message"))
      .def(py::self == py::self)  // NOLINT(misc-redundant-expression)
      .def_readonly("code", &BatchElementError::code)
      .def_readonly("message", &BatchElementError::message);
}
