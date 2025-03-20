// SPDX-License-Identifier: Apache-2.0
// Copyright 2022-2025 The Foundry Visionmongers Ltd
#include <openassetio/hostApi/ManagerFactory.hpp>

#include <cstdlib>
#include <exception>
#include <filesystem>
#include <string>
#include <string_view>
#include <utility>

#include <fmt/core.h>
#include <toml++/toml.h>

#include <openassetio/export.h>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/typedefs.hpp>

namespace {
constexpr std::string_view kConfigDirVar = "${config_dir}";
}  // namespace

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

const Str ManagerFactory::kDefaultManagerConfigEnvVarName = "OPENASSETIO_DEFAULT_CONFIG";

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
    // We leave this as a debug message, as it is expected many hosts
    // will call this by default, and handle a null return manager, vs
    // it being a warning/error.
    logger->debug(fmt::format("{} not set, unable to instantiate default manager.",
                              kDefaultManagerConfigEnvVarName));
    return nullptr;
  }
  logger->debug(fmt::format("Retrieved default manager config file path from '{}'",
                            kDefaultManagerConfigEnvVarName));

  return defaultManagerForInterface(configPath, hostInterface, managerImplementationFactory,
                                    logger);
}

ManagerPtr ManagerFactory::defaultManagerForInterface(
    const std::string_view configPath, const HostInterfacePtr& hostInterface,
    const ManagerImplementationFactoryInterfacePtr& managerImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  logger->debug(fmt::format("Loading default manager config at '{}'", configPath));

  if (!std::filesystem::exists(configPath)) {
    throw errors::InputValidationException(fmt::format(
        "Could not load default manager config from '{}', file does not exist.", configPath));
  }

  if (std::filesystem::is_directory(configPath)) {
    throw errors::InputValidationException(fmt::format(
        "Could not load default manager config from '{}', must be a TOML file not a directory.",
        configPath));
  }

  toml::parse_result config;
  try {
    config = toml::parse_file(configPath);
  } catch (const std::exception& exc) {
    throw errors::ConfigurationException{fmt::format("Error parsing config file. {}", exc.what())};
  }
  const std::string_view identifier = config["manager"]["identifier"].value_or("");

  // Function to substitute ${config_dir} with the absolute,
  // canonicalised directory of the TOML config file.
  const auto substituteConfigDir =
      [configDir =
           std::filesystem::canonical(configPath).parent_path().string()](std::string str) {
        // Adapted from https://en.cppreference.com/w/cpp/string/basic_string/replace
        for (std::string::size_type pos{};
             (pos = str.find(kConfigDirVar, pos)) != std::string::npos;
             pos += configDir.length()) {
          str.replace(pos, kConfigDirVar.length(), configDir);
        }
        return str;
      };

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
        settings.insert({Str{key}, substituteConfigDir(val.as_string()->get())});
      } else if (val.is_boolean()) {
        settings.insert({Str{key}, val.as_boolean()->get()});
      } else {
        throw errors::ConfigurationException(
            fmt::format("Unsupported value type for '{}'.", key.str()));
      }
    }
  }

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
