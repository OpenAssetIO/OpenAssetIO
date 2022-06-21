// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/managerApi/HostSession.h>
#include <openassetio/export.h>

#include <openassetio/managerApi/HostSession.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::managerApi {
using SharedHostSession =
    Converter<openassetio::managerApi::HostSessionPtr, oa_managerApi_SharedHostSession_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
