// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/hostAPI/Manager.h>
#include <openassetio/export.h>

#include <openassetio/hostAPI/Manager.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::hostAPI {
using SharedManager = Converter<openassetio::hostAPI::ManagerPtr, oa_hostAPI_Manager_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
