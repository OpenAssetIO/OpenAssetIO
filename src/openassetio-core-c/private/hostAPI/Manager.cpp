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
#include <openassetio/managerAPI/HostSession.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>

#include "../StringView.hpp"
#include "../errors.hpp"
#include "../handles/InfoDictionary.hpp"
#include "../handles/hostAPI/Manager.hpp"
#include "../handles/managerAPI/HostSession.hpp"
#include "../handles/managerAPI/ManagerInterface.hpp"
#include "openassetio/c/managerAPI/HostSession.h"

namespace errors = openassetio::errors;
namespace handles = openassetio::handles;
namespace hostAPI = openassetio::hostAPI;
namespace managerAPI = openassetio::managerAPI;

extern "C" {

oa_ErrorCode oa_hostAPI_Manager_ctor(oa_StringView* err, oa_hostAPI_Manager_h* handle,
                                     oa_managerAPI_SharedManagerInterface_h managerInterfaceHandle,
                                     oa_managerAPI_SharedHostSession_h hostSessionHandle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    managerAPI::ManagerInterfacePtr& managerInterfacePtr =
        *handles::managerAPI::SharedManagerInterface::toInstance(managerInterfaceHandle);

    managerAPI::HostSessionPtr& hostSessionPtr =
        *handles::managerAPI::SharedHostSession::toInstance(hostSessionHandle);

    auto* manager = new hostAPI::ManagerPtr;
    *manager = std::make_shared<hostAPI::Manager>(managerInterfacePtr, hostSessionPtr);
    *handle = handles::hostAPI::SharedManager::toHandle(manager);

    return oa_ErrorCode_kOK;
  });
}

void oa_hostAPI_Manager_dtor(oa_hostAPI_Manager_h handle) {
  delete handles::hostAPI::SharedManager::toInstance(handle);
}

oa_ErrorCode oa_hostAPI_Manager_identifier(oa_StringView* err, oa_StringView* out,
                                           oa_hostAPI_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostAPI::ManagerPtr manager = *handles::hostAPI::SharedManager::toInstance(handle);
    openassetio::assignStringView(out, manager->identifier());

    return oa_ErrorCode_kOK;
  });
}

oa_ErrorCode oa_hostAPI_Manager_displayName(oa_StringView* err, oa_StringView* out,
                                            oa_hostAPI_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostAPI::ManagerPtr manager = *handles::hostAPI::SharedManager::toInstance(handle);
    openassetio::assignStringView(out, manager->displayName());

    return oa_ErrorCode_kOK;
  });
}

oa_ErrorCode oa_hostAPI_Manager_info(oa_StringView* err, oa_InfoDictionary_h out,
                                     oa_hostAPI_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    openassetio::InfoDictionary* outDict = handles::InfoDictionary::toInstance(out);
    const hostAPI::ManagerPtr manager = *handles::hostAPI::SharedManager::toInstance(handle);

    *outDict = manager->info();

    return oa_ErrorCode_kOK;
  });
}
}  // extern "C"
