// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
#include <ostream>

#include <fmt/core.h>

#include <openassetio/export.h>
#include <openassetio/Context.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/utils/ostream.hpp>

#include "formatter.hpp"

#define OSTREAM_FMT_DEFINITION(Type)                                     \
  std::ostream &operator<<(std::ostream &out, const Type &formattable) { \
    out << fmt::format("{}", formattable);                               \
    return out;                                                          \
  }

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
OSTREAM_FMT_DEFINITION(EntityReference)
OSTREAM_FMT_DEFINITION(EntityReferences)
OSTREAM_FMT_DEFINITION(ContextPtr)
OSTREAM_FMT_DEFINITION(ContextConstPtr)
OSTREAM_FMT_DEFINITION(Context)

namespace managerApi {
OSTREAM_FMT_DEFINITION(ManagerInterface::Capability)
}  // namespace managerApi

namespace hostApi {
OSTREAM_FMT_DEFINITION(Manager::Capability)
}

namespace errors {
OSTREAM_FMT_DEFINITION(BatchElementError)
OSTREAM_FMT_DEFINITION(BatchElementError::ErrorCode)
}  // namespace errors

namespace trait {
OSTREAM_FMT_DEFINITION(TraitsDataPtr)

OSTREAM_FMT_DEFINITION(TraitsDataConstPtr)

OSTREAM_FMT_DEFINITION(TraitsData)

namespace property {
OSTREAM_FMT_DEFINITION(Value)
}
}  // namespace trait
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio

namespace std {
OSTREAM_FMT_DEFINITION(openassetio::StrMap)
OSTREAM_FMT_DEFINITION(openassetio::InfoDictionary)
OSTREAM_FMT_DEFINITION(openassetio::trait::TraitSet)
OSTREAM_FMT_DEFINITION(openassetio::trait::TraitSets)
}  // namespace std
