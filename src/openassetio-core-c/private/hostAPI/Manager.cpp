// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <stdexcept>

#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/hostAPI/Manager.h>
#include <openassetio/c/managerAPI/ManagerInterface.h>
#include <openassetio/c/namespace.h>

#include <openassetio/hostAPI/Manager.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>

#include "../StringView.hpp"
#include "../errors.hpp"
#include "../handles.hpp"

namespace {
using openassetio::hostAPI::Manager;
using openassetio::managerAPI::ManagerInterfacePtr;

using ManagerInterfaceHandleConverter =
    openassetio::handles::Converter<ManagerInterfacePtr,
                                    OPENASSETIO_NS(managerAPI_ManagerInterface_h)>;
using ManagerHandleConverter =
    openassetio::handles::Converter<Manager, OPENASSETIO_NS(hostAPI_Manager_h)>;
}  // namespace

extern "C" {

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_ctor)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(hostAPI_Manager_h) * handle,
 OPENASSETIO_NS(managerAPI_ManagerInterface_h) managerInterfaceHandle) {
  return openassetio::errors::catchUnknownExceptionAsCode(err, [&] {
    auto& managerInterfacePtr =
        *ManagerInterfaceHandleConverter::toInstance(managerInterfaceHandle);

    auto* manager = new Manager{managerInterfacePtr};

    *handle = ManagerHandleConverter::toHandle(manager);

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

void OPENASSETIO_NS(hostAPI_Manager_dtor)(OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  delete ManagerHandleConverter::toInstance(handle);
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_identifier)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return openassetio::errors::catchUnknownExceptionAsCode(err, [&] {
    const auto* manager = ManagerHandleConverter::toInstance(handle);
    openassetio::assignStringView(out, manager->identifier());

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_displayName)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return openassetio::errors::catchUnknownExceptionAsCode(err, [&] {
    const auto* manager = ManagerHandleConverter::toInstance(handle);
    openassetio::assignStringView(out, manager->displayName());

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_info)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return openassetio::errors::catchUnknownExceptionAsCode(err, [&] {
    using InfoDictHandleConverter =
        openassetio::handles::Converter<openassetio::InfoDictionary,
                                        OPENASSETIO_NS(InfoDictionary_h)>;

    auto* outDict = InfoDictHandleConverter::toInstance(out);
    const auto* manager = ManagerHandleConverter::toInstance(handle);

    *outDict = manager->info();

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}
}  // extern "C"
