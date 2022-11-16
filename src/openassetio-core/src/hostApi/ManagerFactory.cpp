// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#include <cstdlib>
#include <filesystem>

#include <toml++/toml.h>

#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>
#include "openassetio/InfoDictionary.hpp"

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

const Str ManagerFactory::kDefaultManagerConfigEnvVarName = "OPENASSETIO_DEFAULT_CONFIG";

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

ManagerPtr ManagerFactory::defaultManagerForInterface(
    const HostInterfacePtr& hostInterface,
    const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  const char* configPath = std::getenv(kDefaultManagerConfigEnvVarName.c_str());

  if (!configPath) {
    Str msg = kDefaultManagerConfigEnvVarName + " not set, unable to instantiate default manager.";
    // We leave this as a debug message, as it is expected may hosts
    // will call this by default, and handle a null return manager, vs
    // it being a warning/error.
    logger->log(log::LoggerInterface::Severity::kDebug, msg);
    return nullptr;
  }

  {
    Str msg = "Loading default manager config from '";
    msg += configPath;
    msg += "' [" + kDefaultManagerConfigEnvVarName + "]";
    logger->log(log::LoggerInterface::Severity::kDebug, msg);
  }

  if (!std::filesystem::exists(configPath)) {
    Str msg = "Could not load default manager config from '";
    msg += configPath;
    msg += "', file does not exist.";
    throw std::runtime_error(msg);
  }

  auto config = toml::parse_file(configPath);

  const std::string_view identifier = config["manager"]["identifier"].value_or("");

  InfoDictionary settings;
  if (toml::table* settingsTable = config["manager"]["settings"].as_table()) {
    // It'd be nice to use settingsTable::for_each, a lambda and
    // w/constexpr to filter supported types, filter, but it ends up
    // being somewhat verbose due to the number of types supported by
    // the variant.
    for (const auto& [key, val] : *settingsTable) {
      if (val.is_integer()) {
        settings.insert({Str{key}, val.as_integer()->get()});
      } else if (val.is_floating_point()) {
        settings.insert({Str{key}, val.as_floating_point()->get()});
      } else if (val.is_string()) {
        settings.insert({Str{key}, val.as_string()->get()});
      } else if (val.is_boolean()) {
        settings.insert({Str{key}, val.as_boolean()->get()});
      } else {
        Str msg = "Unsupported value type for '";
        msg += key.str();
        msg += "'.";
        throw std::runtime_error(msg);
      }
    }
  }

  managerApi::HostSessionPtr hostSession =
      managerApi::HostSession::make(managerApi::Host::make(hostInterface), logger);

  ManagerPtr manager = Manager::make(
      managerImplementationFactory->instantiate(Identifier(identifier)), hostSession);

  manager->initialize(settings);
  return manager;
}
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
