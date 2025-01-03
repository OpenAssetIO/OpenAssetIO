// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <memory>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/trait/TraitsData.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
ContextPtr Context::make(trait::TraitsDataPtr locale,
                         managerApi::ManagerStateBasePtr managerState) {
  return std::shared_ptr<Context>(new Context(std::move(locale), std::move(managerState)));
}

Context::Context(trait::TraitsDataPtr locale_, managerApi::ManagerStateBasePtr managerState_)
    : locale{std::move(locale_)}, managerState{std::move(managerState_)} {}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
