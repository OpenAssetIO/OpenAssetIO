// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/eval.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/errors/exceptions.hpp>

#include "../_openassetio.hpp"

namespace {
void registerNonBatchExceptions(const py::module &mod) {
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

void registerBatchElementException(const py::module &mod) {
  // Pybind has very limited support for custom exception types. This is
  // a well-known tricky issue and is apparently not on the roadmap to
  // fix. The only direct support is for an exception type that takes a
  // single string parameter (message). However, we need `index` and
  // `error` parameters to mirror C++.
  //
  // A way forward is provided by the sketch in:
  // https://github.com/pybind/pybind11/issues/1281#issuecomment-1375950333
  //
  // We execute a Python string literal to create our exception
  // type. The `globals` and `locals` dict parameters dictate the scope
  // of execution, so we use this to ensure the definition is scoped to
  // our `_openassetio` module.

  py::exec(R"pybind(
class BatchElementException(OpenAssetIOException):
    def __init__(self, index: int, error, message: str):
        self.index = index
        self.error = error
        self.message = message
        super().__init__(message))pybind",
           mod.attr("__dict__"), mod.attr("__dict__"));

  // Retrieve a handle the the exception type just created by executing
  // the string literal above.
  const py::object pyBatchElementException = mod.attr("BatchElementException");

  using openassetio::errors::BatchElementException;

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
      const py::object pyInstance = pyClass(exc.index, exc.error, exc.what());
      PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());
    };

    // Handle the different possible C++ exceptions, creating the
    // corresponding Python exception and setting it as the active
    // exception in this thread.
    try {
      std::rethrow_exception(std::move(pexc));
    } catch (const BatchElementException &exc) {
      setPyException("BatchElementException", exc);
    }
  });
}
}  // namespace

void registerExceptions(const py::module &mod) {
  registerNonBatchExceptions(mod);
  // Make sure the non batch exception is registered first, as that
  // includes the shared base exception.
  registerBatchElementException(mod);
}
