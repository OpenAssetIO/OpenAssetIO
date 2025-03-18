// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <utility>

#include <openassetio/export.h>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

UIDelegateImplementationFactoryInterface::~UIDelegateImplementationFactoryInterface() = default;

UIDelegateImplementationFactoryInterface::UIDelegateImplementationFactoryInterface(
    log::LoggerInterfacePtr logger)
    : logger_{std::move(logger)} {}

const log::LoggerInterfacePtr& UIDelegateImplementationFactoryInterface::logger() const {
  return logger_;
}
}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
