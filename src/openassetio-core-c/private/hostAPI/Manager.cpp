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
#include "../handles/InfoDictionary.hpp"
#include "../handles/hostAPI/Manager.hpp"
#include "../handles/managerAPI/ManagerInterface.hpp"

namespace errors = openassetio::errors;
namespace handles = openassetio::handles;
namespace hostAPI = openassetio::hostAPI;
namespace managerAPI = openassetio::managerAPI;

extern "C" {

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_ctor)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(hostAPI_Manager_h) * handle,
 OPENASSETIO_NS(managerAPI_SharedManagerInterface_h) managerInterfaceHandle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    managerAPI::ManagerInterfacePtr& managerInterfacePtr =
        *handles::managerAPI::SharedManagerInterface::toInstance(managerInterfaceHandle);

    auto* manager = new hostAPI::Manager{managerInterfacePtr};

    *handle = handles::hostAPI::Manager::toHandle(manager);

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

void OPENASSETIO_NS(hostAPI_Manager_dtor)(OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  delete handles::hostAPI::Manager::toInstance(handle);
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_identifier)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostAPI::Manager* manager = handles::hostAPI::Manager::toInstance(handle);
    openassetio::assignStringView(out, manager->identifier());

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_displayName)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostAPI::Manager* manager = handles::hostAPI::Manager::toInstance(handle);
    openassetio::assignStringView(out, manager->displayName());

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}

OPENASSETIO_NS(ErrorCode)
OPENASSETIO_NS(hostAPI_Manager_info)
(OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) out,
 OPENASSETIO_NS(hostAPI_Manager_h) handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    openassetio::InfoDictionary* outDict = handles::InfoDictionary::toInstance(out);
    const hostAPI::Manager* manager = handles::hostAPI::Manager::toInstance(handle);

    *outDict = manager->info();

    return OPENASSETIO_NS(ErrorCode_kOK);
  });
}
}  // extern "C"
