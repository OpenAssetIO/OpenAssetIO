// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd

#include <openassetio/EntityReference.hpp>
#include <openassetio/hostApi/EntityReferencePager.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/HostSession.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

typename EntityReferencePager::Ptr EntityReferencePager::make(
    managerApi::EntityReferencePagerInterfacePtr pagerInterface,
    managerApi::HostSessionPtr hostSession) {
  return EntityReferencePager::Ptr{
      new EntityReferencePager{std::move(pagerInterface), std::move(hostSession)}};
}

EntityReferencePager::EntityReferencePager(
    managerApi::EntityReferencePagerInterfacePtr pagerInterface,
    managerApi::HostSessionPtr hostSession)
    : pagerInterface_(std::move(pagerInterface)), hostSession_(std::move(hostSession)) {}

EntityReferencePager::~EntityReferencePager() {
  try {
    pagerInterface_->close(hostSession_);
  } catch (const std::exception& ex) {
    hostSession_->logger()->error(ex.what());
  } catch (...) {
    hostSession_->logger()->error(
        "Unknown non-exception object caught during destruction of EntityReferencePager");
  }
}

bool EntityReferencePager::hasNext() { return pagerInterface_->hasNext(hostSession_); }

typename EntityReferencePager::Page EntityReferencePager::get() {
  return pagerInterface_->get(hostSession_);
}

void EntityReferencePager::next() { pagerInterface_->next(hostSession_); }

}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
