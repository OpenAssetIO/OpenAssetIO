// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
/**
 * Bindings used for testing errors behaviour.
 * Specifically, the conversion from cpp -> python.
 *
 * See tests/cmodule/test_errors.py
 */

#include <pybind11/pybind11.h>

#include <openassetio/errors/exceptions.hpp>
namespace py = pybind11;

namespace {
// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
void throwException(const std::string& exceptionName, const std::string& msgData = "") {
  if (exceptionName == "OpenAssetIOException") {
    throw openassetio::errors::OpenAssetIOException(msgData);
  }
  if (exceptionName == "InputValidationException") {
    throw openassetio::errors::InputValidationException(msgData);
  }
  if (exceptionName == "ConfigurationException") {
    throw openassetio::errors::ConfigurationException(msgData);
  }
  if (exceptionName == "NotImplementedException") {
    throw openassetio::errors::NotImplementedException(msgData);
  }
  if (exceptionName == "UnhandledException") {
    throw openassetio::errors::UnhandledException(msgData);
  }
}
}  // namespace

/**
 * Functions to aid testing C++ exceptions and their Python conversion.
 *
 * `throwException` takes an exception by name (matching `cls.__name__`
 * in Python) and throws it, with an optional message. This then allows
 * us to test that C++->Python exception conversion is working as
 * expected.
 *
 * `isThrownExceptionCatchableAs` is a bit of a kludge to allow us to
 * test the C++ exception hierarchy using pytest. The caller provides
 * the name of an exception to throw and the name of a (base class)
 * exception to catch. The function simply returns `True` to Python, or,
 * if the catch failed, allows the exception to propagate (failing the
 * pytest). Note that the exception hierarchy in C++ and in Python are
 * configured independently, so testing one does not test the other.
 */
void registerExceptionThrower(py::module_& mod) {
  mod.def("throwException", [](const std::string& exceptionName, const std::string& msgData) {
    throwException(exceptionName, msgData);
  });
  mod.def(
      "isThrownExceptionCatchableAs",
      [](const std::string& throwExceptionName, const std::string& catchExceptionName) {
        if (catchExceptionName == "OpenAssetIOException") {
          try {
            throwException(throwExceptionName);
          } catch (const openassetio::errors::OpenAssetIOException&) {
            return true;
          }
        }
        if (catchExceptionName == "InputValidationException") {
          try {
            throwException(throwExceptionName);
          } catch (const openassetio::errors::InputValidationException&) {
            return true;
          }
        }
        if (catchExceptionName == "ConfigurationException") {
          try {
            throwException(throwExceptionName);
          } catch (const openassetio::errors::ConfigurationException&) {
            return true;
          }
        }
        if (catchExceptionName == "NotImplementedException") {
          try {
            throwException(throwExceptionName);
          } catch (const openassetio::errors::NotImplementedException&) {
            return true;
          }
        }
        if (catchExceptionName == "UnhandledException") {
          try {
            throwException(throwExceptionName);
          } catch (const openassetio::errors::UnhandledException&) {
            return true;
          }
        }
        return false;
      },
      py::arg("throwExceptionName"), py::arg("catchExceptionName"));
}
