// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/c/InfoDictionary.h>
#include <openassetio/export.h>

#include <openassetio/InfoDictionary.hpp>

#include "Converter.hpp"

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace handles {
using InfoDictionary = Converter<InfoDictionary, oa_InfoDictionary_h>;
}
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
