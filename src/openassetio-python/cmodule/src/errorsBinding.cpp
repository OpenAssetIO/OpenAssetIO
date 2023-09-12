// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/pybind11.h>

#include <openassetio/errors/exceptions.hpp>

#include "_openassetio.hpp"

void registerErrors(const py::module &mod) {
  using openassetio::errors::ConfigurationException;
  using openassetio::errors::InputValidationException;
  using openassetio::errors::NotImplementedException;
  using openassetio::errors::OpenAssetIOException;
  using openassetio::errors::UnhandledException;

  // Register a new exception type. Note that this is not sufficient to
  // cause C++ exceptions to be translated. See
  // `register_exception_translator` below.
  const auto registerPyException = [&mod](const char *pyTypeName, const py::handle &base) {
    return py::exception<void /* unused */>{mod, pyTypeName, base};
  };

  // Register our OpenAssetIO exception types. Since these exceptions
  // simply take a string message and no other data, we can make use
  // of pybind11's limited custom exception support.

  const py::object pyOpenAssetIOException =
      registerPyException("OpenAssetIOException", PyExc_RuntimeError);
  // NOLINTNEXTLINE(bugprone-throw-keyword-missing)
  registerPyException("UnhandledException", pyOpenAssetIOException);
  // NOLINTNEXTLINE(bugprone-throw-keyword-missing)
  registerPyException("NotImplementedException", pyOpenAssetIOException);
  const py::object pyInputValidationException =
      registerPyException("InputValidationException", pyOpenAssetIOException);
  // NOLINTNEXTLINE(bugprone-throw-keyword-missing)
  registerPyException("ConfigurationException", pyInputValidationException);

  // Register a function that will translate our C++ exceptions to the
  // appropriate Python exception type.
  //
  // Note that capturing lambdas are not allowed here, so we must
  // `import` the exception type in the body of the function.
  py::register_exception_translator([](std::exception_ptr pexc) {
    if (!pexc) {
      return;
    }
    const py::module_ pyModule = py::module_::import("openassetio._openassetio.errors");

    // Use CPython's PyErr_SetObject to set a custom exception type as
    // the currently active Python exception in this thread.
    const auto setPyException = [&pyModule](const char *pyTypeName, const auto &exc) {
      const py::object pyClass = pyModule.attr(pyTypeName);
      const py::object pyInstance = pyClass(exc.what());
      PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());
    };

    // Handle the different possible C++ exceptions, creating the
    // corresponding Python exception and setting it as the active
    // exception in this thread.
    try {
      std::rethrow_exception(std::move(pexc));
    } catch (const ConfigurationException &exc) {
      setPyException("ConfigurationException", exc);
    } catch (const InputValidationException &exc) {
      setPyException("InputValidationException", exc);
    } catch (const NotImplementedException &exc) {
      setPyException("NotImplementedException", exc);
    } catch (const UnhandledException &exc) {
      setPyException("UnhandledException", exc);
    } catch (const OpenAssetIOException &exc) {
      setPyException("OpenAssetIOException", exc);
    }
  });
}
