// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

ManagerFactoryPtr ManagerFactory::make(
    HostInterfacePtr hostInterface,
    ManagerImplementationFactoryInterfacePtr managerImplementationFactory,
    log::LoggerInterfacePtr logger) {
  return openassetio::hostApi::ManagerFactoryPtr{new ManagerFactory{
      std::move(hostInterface), std::move(managerImplementationFactory), std::move(logger)}};
}

ManagerFactory::ManagerFactory(
    HostInterfacePtr hostInterface,
    ManagerImplementationFactoryInterfacePtr managerImplementationFactory,
    log::LoggerInterfacePtr logger)
    : hostInterface_{std::move(hostInterface)},
      managerImplementationFactory_{std::move(managerImplementationFactory)},
      logger_{std::move(logger)} {}

Identifiers ManagerFactory::identifiers() const {
  return managerImplementationFactory_->identifiers();
}

ManagerFactory::ManagerDetails ManagerFactory::availableManagers() const {
  const Identifiers& ids = identifiers();
  if (ids.empty()) {
    return {};
  }

  ManagerDetails managerDetails;

  for (const Identifier& identifier : ids) {
    const managerApi::ManagerInterfacePtr managerInterface =
        managerImplementationFactory_->instantiate(identifier);

    managerDetails.insert({identifier,
                           {managerInterface->identifier(), managerInterface->displayName(),
                            managerInterface->info()}});
  }
  return managerDetails;
}

ManagerPtr ManagerFactory::createManager(const Identifier& identifier) const {
  return createManagerForInterface(identifier, hostInterface_, managerImplementationFactory_,
                                   logger_);
}

ManagerPtr ManagerFactory::createManagerForInterface(
    const Identifier& identifier, const HostInterfacePtr& hostInterface,
    const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  return Manager::make(
      managerImplementationFactory->instantiate(identifier),
      managerApi::HostSession::make(managerApi::Host::make(hostInterface), logger));
}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
