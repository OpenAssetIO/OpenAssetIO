// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <any>
#include <memory>
#include <utility>

#include <pybind11/pybind11.h>

#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegateRequestInterface.hpp>
#include <openassetio/ui/hostApi/UIDelegateState.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateRequest.hpp>
#include <openassetio/ui/managerApi/UIDelegateStateInterface.hpp>

namespace py = pybind11;

struct StubUIDelegateRequest : openassetio::ui::hostApi::UIDelegateRequestInterface {
  StubUIDelegateRequest() = default;
  StubUIDelegateRequest(const StubUIDelegateRequest& other) = delete;
  StubUIDelegateRequest(StubUIDelegateRequest&& other) noexcept = default;
  StubUIDelegateRequest& operator=(const StubUIDelegateRequest& other) = delete;
  StubUIDelegateRequest& operator=(StubUIDelegateRequest&& other) noexcept = default;

  ~StubUIDelegateRequest() override {
    if (nativeData_.has_value()) {
      try {
        auto gil = py::gil_scoped_acquire{};
        (void)py::handle{std::any_cast<PyObject*>(nativeData_)}.dec_ref();
      } catch (...) {  // NOLINT(*-empty-catch)
        // ?
      }
    }
  }

  [[nodiscard]] std::any nativeData() override { return nativeData_; }
  std::any nativeData_;
};

struct StubUIDelegateState : openassetio::ui::managerApi::UIDelegateStateInterface {
  StubUIDelegateState() = default;
  StubUIDelegateState(const StubUIDelegateState& other) = delete;
  StubUIDelegateState(StubUIDelegateState&& other) noexcept = default;
  StubUIDelegateState& operator=(const StubUIDelegateState& other) = delete;
  StubUIDelegateState& operator=(StubUIDelegateState&& other) noexcept = default;

  ~StubUIDelegateState() override {
    if (nativeData_.has_value()) {
      try {
        auto gil = py::gil_scoped_acquire{};
        (void)py::handle{std::any_cast<PyObject*>(nativeData_)}.dec_ref();
      } catch (...) {  // NOLINT(*-empty-catch)
        // ?
      }
    }
  }

  [[nodiscard]] std::any nativeData() override { return nativeData_; }
  std::any nativeData_;
};

struct StubUIDelegateInterface : openassetio::ui::managerApi::UIDelegateInterface {
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return "org.openassetio.test.cmodule.stub";
  }

  [[nodiscard]] openassetio::Str displayName() const override { return "Stub UI Delegate"; }
};

extern void registerUIDelegateTestTypes(py::module& mod) {
  using openassetio::ui::hostApi::UIDelegateRequestInterfacePtr;
  using openassetio::ui::hostApi::UIDelegateState;
  using openassetio::ui::managerApi::UIDelegateInterfacePtr;
  using openassetio::ui::managerApi::UIDelegateRequest;
  using openassetio::ui::managerApi::UIDelegateStateInterfacePtr;

  auto ui = mod.def_submodule("ui");
  ui.def("createUIDelegateRequestInterfaceWithNonPyObjectNativeData",
         []() -> UIDelegateRequestInterfacePtr {
           auto request = std::make_shared<StubUIDelegateRequest>();
           request->nativeData_ = double{};
           return request;
         });
  ui.def("createUIDelegateRequestInterfaceWithRawCPythonNativeData",
         []() -> UIDelegateRequestInterfacePtr {
           auto request = std::make_shared<StubUIDelegateRequest>();
           request->nativeData_ = PyLong_FromLong(42);  // NOLINT
           return request;
         });
  ui.def("createUIDelegateStateInterfaceWithNonPyObjectNativeData",
         []() -> UIDelegateStateInterfacePtr {
           auto state = std::make_shared<StubUIDelegateState>();
           state->nativeData_ = double{};
           return state;
         });
  ui.def("createUIDelegateStateInterfaceWithRawCPythonNativeData",
         []() -> UIDelegateStateInterfacePtr {
           auto state = std::make_shared<StubUIDelegateState>();
           state->nativeData_ = PyLong_FromLong(42);  // NOLINT
           return state;
         });
  ui.def("createUIDelegateRequestWithNonPyObjectNativeData", []() -> UIDelegateRequest::Ptr {
    auto request = std::make_shared<StubUIDelegateRequest>();
    request->nativeData_ = double{};
    return UIDelegateRequest::make(std::move(request));
  });
  ui.def("createUIDelegateRequestWithRawCPythonNativeData", []() -> UIDelegateRequest::Ptr {
    auto request = std::make_shared<StubUIDelegateRequest>();
    request->nativeData_ = PyLong_FromLong(42);  // NOLINT
    return UIDelegateRequest::make(std::move(request));
  });
  ui.def("createUIDelegateStateWithNonPyObjectNativeData", []() -> UIDelegateState::Ptr {
    auto state = std::make_shared<StubUIDelegateState>();
    state->nativeData_ = double{};
    return UIDelegateState::make(std::move(state));
  });
  ui.def("createUIDelegateStateWithRawCPythonNativeData", []() -> UIDelegateState::Ptr {
    auto state = std::make_shared<StubUIDelegateState>();
    state->nativeData_ = PyLong_FromLong(42);  // NOLINT
    return UIDelegateState::make(std::move(state));
  });
  ui.def("createCppUIDelegateInterface",
         []() -> UIDelegateInterfacePtr { return std::make_shared<StubUIDelegateInterface>(); });
}
