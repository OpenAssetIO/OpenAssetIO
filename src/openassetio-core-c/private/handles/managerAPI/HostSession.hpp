// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/managerAPI/HostSession.h>
#include <openassetio/export.h>

#include <openassetio/managerAPI/HostSession.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::managerAPI {
using SharedHostSession =
    Converter<openassetio::managerAPI::HostSessionPtr, oa_managerAPI_SharedHostSession_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
