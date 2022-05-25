// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/managerAPI/ManagerInterface.h>
#include <openassetio/export.h>

#include <openassetio/managerAPI/ManagerInterface.hpp>

#include "../Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace handles::managerAPI {
using SharedManagerInterface = Converter<openassetio::managerAPI::ManagerInterfacePtr,
                                         oa_managerAPI_SharedManagerInterface_h>;
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
