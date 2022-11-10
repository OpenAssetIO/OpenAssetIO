// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/managerApi/ManagerInterface.h>
#include <openassetio/export.h>

#include <openassetio/managerApi/ManagerInterface.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::managerApi {
using SharedManagerInterface = Converter<openassetio::managerApi::ManagerInterfacePtr,
                                         oa_managerApi_SharedManagerInterface_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
