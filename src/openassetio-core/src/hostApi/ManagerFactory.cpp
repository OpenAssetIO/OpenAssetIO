// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/ManagerFactory.hpp>

#include <cstdlib>
#include <string_view>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/private/hostApi/factory.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

const Str ManagerFactory::kDefaultManagerConfigEnvVarName{factory::kDefaultConfigEnvVarName};

ManagerFactoryPtr ManagerFactory::make(
    HostInterfacePtr hostInterface,
    ManagerImplementationFactoryInterfacePtr managerImplementationFactory,
    log::LoggerInterfacePtr logger) {
  return ManagerFactoryPtr{new ManagerFactory{
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
  return factory::queryBasicDetails<ManagerDetail>(managerImplementationFactory_);
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

ManagerPtr ManagerFactory::defaultManagerForInterface(
    const HostInterfacePtr& hostInterface,
    const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  if (const char* configPath =
          factory::configPathFromEnvVar(logger, kDefaultManagerConfigEnvVarName)) {
    return defaultManagerForInterface(configPath, hostInterface, managerImplementationFactory,
                                      logger);
  }
  return nullptr;
}

ManagerPtr ManagerFactory::defaultManagerForInterface(
    const std::string_view configPath, const HostInterfacePtr& hostInterface,
    const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  const auto& [identifier, settings] =
      factory::identifierAndSettingsFromConfigFile(logger, configPath, "manager");

  const managerApi::HostSessionPtr hostSession =
      managerApi::HostSession::make(managerApi::Host::make(hostInterface), logger);

  const ManagerPtr manager = Manager::make(
      managerImplementationFactory->instantiate(Identifier(identifier)), hostSession);

  manager->initialize(settings);
  return manager;
}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
