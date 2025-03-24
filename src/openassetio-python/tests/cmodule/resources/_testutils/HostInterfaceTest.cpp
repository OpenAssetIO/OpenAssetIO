// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <memory>

#include <pybind11/pybind11.h>

#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace py = pybind11;

class StubHostInterface final : public openassetio::hostApi::HostInterface {
 public:
  [[nodiscard]] openassetio::Identifier identifier() const override {
    return "org.openassetio.host.stub";
  }
  [[nodiscard]] openassetio::Str displayName() const override { return "Stub Host"; }
};

extern void registerCreateHostInterface(py::module& mod) {
  using openassetio::hostApi::HostInterfacePtr;

  mod.def("createCppHostInterface",
          []() -> HostInterfacePtr { return std::make_shared<StubHostInterface>(); });
}
