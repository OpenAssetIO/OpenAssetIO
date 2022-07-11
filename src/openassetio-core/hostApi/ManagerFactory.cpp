// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/LoggerInterface.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerInterfaceFactoryInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

ManagerFactoryPtr ManagerFactory::make(HostInterfacePtr hostInterface,
                                       ManagerInterfaceFactoryInterfacePtr managerInterfaceFactory,
                                       LoggerInterfacePtr logger) {
  return openassetio::hostApi::ManagerFactoryPtr{new ManagerFactory{
      std::move(hostInterface), std::move(managerInterfaceFactory), std::move(logger)}};
}

ManagerFactory::ManagerFactory(HostInterfacePtr hostInterface,
                               ManagerInterfaceFactoryInterfacePtr managerInterfaceFactory,
                               LoggerInterfacePtr logger)
    : hostInterface_{std::move(hostInterface)},
      managerInterfaceFactory_{std::move(managerInterfaceFactory)},
      logger_{std::move(logger)} {}

Identifiers ManagerFactory::identifiers() const { return managerInterfaceFactory_->identifiers(); }

ManagerFactory::ManagerDetails ManagerFactory::availableManagers() const {
  const Identifiers& ids = identifiers();
  if (ids.empty()) {
    return {};
  }

  // `HostSession` required for `settings()` calls.
  const managerApi::HostSessionPtr hostSession =
      managerApi::HostSession::make(managerApi::Host::make(hostInterface_));

  ManagerDetails managerDetails;

  for (const Identifier& identifier : ids) {
    const managerApi::ManagerInterfacePtr managerInterface =
        managerInterfaceFactory_->instantiate(identifier);

    managerDetails.insert({identifier,
                           {managerInterface->identifier(), managerInterface->displayName(),
                            managerInterface->info()}});
  }
  return managerDetails;
}

ManagerPtr ManagerFactory::createManager(const Identifier& identifier) const {
  return createManagerForInterface(identifier, hostInterface_, managerInterfaceFactory_, logger_);
}

ManagerPtr ManagerFactory::createManagerForInterface(
    const Identifier& identifier, const HostInterfacePtr& hostInterface,
    const ManagerInterfaceFactoryInterfacePtr& managerInterfaceFactory,
    [[maybe_unused]] const LoggerInterfacePtr& logger) {
  return Manager::make(managerInterfaceFactory->instantiate(identifier),
                       managerApi::HostSession::make(managerApi::Host::make(hostInterface)));
}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
