// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/hostAPI/Manager.hpp>
#include <openassetio/managerAPI/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostAPI {

Manager::Manager(managerAPI::ManagerInterfacePtr managerInterface,
                 managerAPI::HostSessionPtr hostSession)
    : managerInterface_{std::move(managerInterface)}, hostSession_{std::move(hostSession)} {}

Str Manager::identifier() const { return managerInterface_->identifier(); }

Str Manager::displayName() const { return managerInterface_->displayName(); }

InfoDictionary Manager::info() const { return managerInterface_->info(); }

void Manager::initialize() { managerInterface_->initialize(hostSession_); }

ContextPtr Manager::createContext() {
  ContextPtr context = openassetio::makeShared<Context>();
  context->managerState = managerInterface_->createState(hostSession_);
  return context;
}

ContextPtr Manager::createChildContext(const ContextPtr &parentContext) {
  ContextPtr context = openassetio::makeShared<Context>();
  context->access = parentContext->access;
  context->retention = parentContext->retention;
  context->locale = parentContext->locale;
  if (parentContext->managerState) {
    context->managerState =
        managerInterface_->createChildState(parentContext->managerState, hostSession_);
  }
  return context;
}

std::string Manager::persistenceTokenForContext(const ContextPtr &context) {
  if (context->managerState) {
    return managerInterface_->persistenceTokenForState(context->managerState, hostSession_);
  }
  return "";
}

ContextPtr Manager::contextFromPersistenceToken(const std::string &token) {
  ContextPtr context = openassetio::makeShared<Context>();
  if (!token.empty()) {
    context->managerState = managerInterface_->stateFromPersistenceToken(token, hostSession_);
  }
  return context;
}

}  // namespace hostAPI
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
