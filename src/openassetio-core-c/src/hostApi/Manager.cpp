// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2025 The Foundry Visionmongers Ltd
#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/hostApi/Manager.h>
#include <openassetio/c/managerApi/HostSession.h>
#include <openassetio/c/managerApi/ManagerInterface.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>

#include "../StringView.hpp"
#include "../errors.hpp"
#include "../handles/InfoDictionary.hpp"
#include "../handles/hostApi/Manager.hpp"
#include "../handles/managerApi/HostSession.hpp"
#include "../handles/managerApi/ManagerInterface.hpp"

namespace errors = openassetio::errors;
namespace handles = openassetio::handles;
namespace hostApi = openassetio::hostApi;
namespace managerApi = openassetio::managerApi;

extern "C" {

oa_ErrorCode oa_hostApi_Manager_ctor(oa_StringView* err, oa_hostApi_Manager_h* handle,
                                     oa_managerApi_SharedManagerInterface_h managerInterfaceHandle,
                                     oa_managerApi_SharedHostSession_h hostSessionHandle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const managerApi::ManagerInterfacePtr& managerInterfacePtr =
        *handles::managerApi::SharedManagerInterface::toInstance(managerInterfaceHandle);

    const managerApi::HostSessionPtr& hostSessionPtr =
        *handles::managerApi::SharedHostSession::toInstance(hostSessionHandle);

    auto* manager = new hostApi::ManagerPtr;
    *manager = hostApi::Manager::make(managerInterfacePtr, hostSessionPtr);
    *handle = handles::hostApi::SharedManager::toHandle(manager);

    return oa_ErrorCode_kOK;
  });
}

void oa_hostApi_Manager_dtor(oa_hostApi_Manager_h handle) {
  delete handles::hostApi::SharedManager::toInstance(handle);
}

oa_ErrorCode oa_hostApi_Manager_identifier(oa_StringView* err, oa_StringView* out,
                                           oa_hostApi_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostApi::ManagerPtr manager = *handles::hostApi::SharedManager::toInstance(handle);
    openassetio::assignStringView(out, manager->identifier());

    return oa_ErrorCode_kOK;
  });
}

oa_ErrorCode oa_hostApi_Manager_displayName(oa_StringView* err, oa_StringView* out,
                                            oa_hostApi_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    const hostApi::ManagerPtr manager = *handles::hostApi::SharedManager::toInstance(handle);
    openassetio::assignStringView(out, manager->displayName());

    return oa_ErrorCode_kOK;
  });
}

oa_ErrorCode oa_hostApi_Manager_info(oa_StringView* err, oa_InfoDictionary_h out,
                                     oa_hostApi_Manager_h handle) {
  return errors::catchUnknownExceptionAsCode(err, [&] {
    openassetio::InfoDictionary* outDict = handles::InfoDictionary::toInstance(out);
    const hostApi::ManagerPtr manager = *handles::hostApi::SharedManager::toInstance(handle);

    *outDict = manager->info();

    return oa_ErrorCode_kOK;
  });
}
}  // extern "C"
