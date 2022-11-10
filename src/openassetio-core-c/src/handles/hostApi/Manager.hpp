// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/hostApi/Manager.h>
#include <openassetio/export.h>

#include <openassetio/hostApi/Manager.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::hostApi {
using SharedManager = Converter<openassetio::hostApi::ManagerPtr, oa_hostApi_Manager_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
