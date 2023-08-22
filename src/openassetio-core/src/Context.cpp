// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/Context.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
ContextPtr Context::make(Access access, TraitsDataPtr locale,
                         managerApi::ManagerStateBasePtr managerState) {
  return std::shared_ptr<Context>(new Context(access, std::move(locale), std::move(managerState)));
}

Context::Context(Access access_, TraitsDataPtr locale_,
                 managerApi::ManagerStateBasePtr managerState_)
    : access{access_}, locale{std::move(locale_)}, managerState{std::move(managerState_)} {}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
