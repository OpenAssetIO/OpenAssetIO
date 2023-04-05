// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <string_view>

#include <pybind11/eval.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <openassetio/BatchElementError.hpp>

#include "_openassetio.hpp"

void registerBatchElementError(py::module &mod) {
  using openassetio::BatchElementError;

  py::class_<BatchElementError> batchElementError{mod, "BatchElementError", py::is_final()};

  py::enum_<BatchElementError::ErrorCode>{batchElementError, "ErrorCode"}
      .value("kUnknown", BatchElementError::ErrorCode::kUnknown)
      .value("kInvalidEntityReference", BatchElementError::ErrorCode::kInvalidEntityReference)
      .value("kMalformedEntityReference", BatchElementError::ErrorCode::kMalformedEntityReference)
      .value("kEntityAccessError", BatchElementError::ErrorCode::kEntityAccessError)
      .value("kEntityResolutionError", BatchElementError::ErrorCode::kEntityResolutionError);

  batchElementError
      .def(py::init<BatchElementError::ErrorCode, openassetio::Str>(), py::arg("code"),
           py::arg("message"))
      .def(py::self == py::self)  // NOLINT(misc-redundant-expression)
      .def_readonly("code", &BatchElementError::code)
      .def_readonly("message", &BatchElementError::message);

  // Pybind has very limited support for custom exception types. This is
  // a well-known tricky issue and is apparently not on the roadmap to
  // fix. The only direct support is for an exception type that takes a
  // single string parameter (message). However, we need `index` and
  // `error` parameters to mirror C++.
  //
  // A way forward is provided by the sketch in:
  // https://github.com/pybind/pybind11/issues/1281#issuecomment-1375950333
  //
  // We execute a Python string literal to create our base exception
  // type. The `globals` and `locals` dict parameters dictate the scope
  // of execution, so we use this to ensure the definition is scoped to
  // our `_openassetio` module.
  //
  // We can then retrieve this base exception type as a pybind object
  // and use it as the base class for pybind's limited exception
  // registration API.

  py::exec(R"pybind(
class BatchElementException(RuntimeError):
    def __init__(self, index: int, error):
        self.index = index
        self.error = error
        super().__init__(error.message))pybind",
           mod.attr("__dict__"), mod.attr("__dict__"));

  // Retrieve a handle the the exception type just created by executing
  // the string literal above.
  const py::object pyBatchElementException = mod.attr("BatchElementException");

  using openassetio::BatchElementException;
  using openassetio::EntityAccessErrorBatchElementException;
  using openassetio::EntityResolutionErrorBatchElementException;
  using openassetio::InvalidEntityReferenceBatchElementException;
  using openassetio::MalformedEntityReferenceBatchElementException;
  using openassetio::UnknownBatchElementException;

  // Register a new exception type using `BatchElementException` base
  // class created above. Note that this is not sufficient to cause C++
  // exceptions to be translated. See `register_exception_translator`
  // below.
  const auto registerPyException = [&mod, &pyBatchElementException](const char *pyTypeName) {
    py::exception<void /* unused */>{mod, pyTypeName, pyBatchElementException};
  };

  // Register each of our BatchElement exception types.
  registerPyException("UnknownBatchElementException");
  registerPyException("InvalidEntityReferenceBatchElementException");
  registerPyException("MalformedEntityReferenceBatchElementException");
  registerPyException("EntityAccessErrorBatchElementException");
  registerPyException("EntityResolutionErrorBatchElementException");

  // Register a function that will translate our C++ exceptions to the
  // appropriate Python exception type.
  //
  // Note that capturing lambdas are not allowed here, so we must
  // `import` the exception type in the body of the function.
  py::register_exception_translator([](std::exception_ptr pexc) {
    if (!pexc) {
      return;
    }
    const py::module_ pyModule = py::module_::import("openassetio._openassetio");

    // Use CPython's PyErr_SetObject to set a custom exception type as
    // the currently active Python exception in this thread.
    const auto setPyException = [&pyModule](const char *pyTypeName, const auto &exc) {
      const py::object pyClass = pyModule.attr(pyTypeName);
      const py::object pyInstance = pyClass(exc.index, exc.error);
      PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());
    };

    // Handle the different possible C++ exceptions, creating the
    // corresponding Python exception and setting it as the active
    // exception in this thread.
    try {
      std::rethrow_exception(std::move(pexc));
    } catch (const UnknownBatchElementException &exc) {
      setPyException("UnknownBatchElementException", exc);
    } catch (const InvalidEntityReferenceBatchElementException &exc) {
      setPyException("InvalidEntityReferenceBatchElementException", exc);
    } catch (const MalformedEntityReferenceBatchElementException &exc) {
      setPyException("MalformedEntityReferenceBatchElementException", exc);
    } catch (const EntityAccessErrorBatchElementException &exc) {
      setPyException("EntityAccessErrorBatchElementException", exc);
    } catch (const EntityResolutionErrorBatchElementException &exc) {
      setPyException("EntityResolutionErrorBatchElementException", exc);
    } catch (const BatchElementException &exc) {
      setPyException("BatchElementException", exc);
    }
  });
}
