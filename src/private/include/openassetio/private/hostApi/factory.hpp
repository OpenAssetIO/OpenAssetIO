// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
/**
 * Common functionality for the host API factory middleware responsible
 * for creating manager or UI delegate interfaces.
 */
#pragma once

#include <filesystem>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>

#include <fmt/core.h>
#include <toml++/toml.h>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi::factory {

constexpr std::string_view kConfigDirVar = "${config_dir}";

constexpr std::string_view kDefaultConfigEnvVarName = "OPENASSETIO_DEFAULT_CONFIG";

/**
 * Query a factory (typically, a plugin system) for the basic details
 * of the implementations it can provide.
 *
 * @tparam Detail Class that is constructible with an identifier,
 * display name and info dict.
 *
 * @tparam ImplFactory Type of factory for listing and (cheaply)
 * instantiating implementations of an interface.
 *
 * @param implFactory Factory for listing and (cheaply) instantiating
 * implementations of an interface.
 *
 * @return A map of identifier to @p Detail instances.
 */
template <class Detail, class ImplFactory>
auto queryBasicDetails(const ImplFactory& implFactory) {
  std::unordered_map<Identifier, Detail> details;

  for (const Identifier& identifier : implFactory->identifiers()) {
    const auto impl = implFactory->instantiate(identifier);

    details.insert({identifier, {impl->identifier(), impl->displayName(), impl->info()}});
  }
  return details;
}

/**
 * Retrieve a path to a configuration file from an environment variable,
 * and log success or failure.
 *
 * @param logger Logger to report progress or issues.
 *
 * @param envVarName Name of environment variable to query.
 *
 * @return Path retrieved from environment variable, or nullptr.
 */
inline const char* configPathFromEnvVar(const log::LoggerInterfacePtr& logger,
                                        const std::string_view envVarName) {
  // NOLINTNEXTLINE(bugprone-suspicious-stringview-data-usage)
  const char* configPath = std::getenv(envVarName.data());

  if (!configPath) {
    // We leave this as a debug message, as it is expected many hosts
    // will call this by default, and handle a null return manager, vs
    // it being a warning/error.
    logger->debug(fmt::format("{} not set, unable to instantiate default instance", envVarName));
    return nullptr;
  }
  logger->debug(fmt::format("Retrieved default config file path from '{}'", envVarName));

  return configPath;
}

/**
 * Extract the identifier and settings from a TOML-formatted config
 * file.
 *
 * @param logger Logger to log progress.
 *
 * @param configPath Path to config file.
 *
 * @param settingsKey Top-level key from which to retrieve settings.
 *
 * @return Pair of identifier and settings to use when selecting and
 * instantiating from a factory (i.e. plugin system).
 */
inline std::pair<Identifier, InfoDictionary> identifierAndSettingsFromConfigFile(
    const log::LoggerInterfacePtr& logger, const std::filesystem::path& configPath,
    const std::string_view settingsKey) {
  logger->debug(fmt::format("Loading default config at '{}'", configPath.u8string()));

  if (!exists(configPath)) {
    throw errors::InputValidationException(fmt::format(
        "Could not load default config from '{}', file does not exist.", configPath.u8string()));
  }

  if (is_directory(configPath)) {
    throw errors::InputValidationException(fmt::format(
        "Could not load default config from '{}', must be a TOML file not a directory.",
        configPath.u8string()));
  }

  toml::parse_result config;
  try {
    config = toml::parse_file(configPath.u8string());
  } catch (const std::exception& exc) {
    throw errors::ConfigurationException{fmt::format("Error parsing config file. {}", exc.what())};
  }
  const std::string_view identifier = config["manager"]["identifier"].value_or("");

  // Function to substitute ${config_dir} with the absolute,
  // canonicalised directory of the TOML config file.
  const auto substituteConfigDir = [configDir = canonical(configPath).parent_path().string()](
                                       std::string str) {
    // Adapted from https://en.cppreference.com/w/cpp/string/basic_string/replace
    for (std::string::size_type pos{}; (pos = str.find(kConfigDirVar, pos)) != std::string::npos;
         pos += configDir.length()) {
      str.replace(pos, kConfigDirVar.length(), configDir);
    }
    return str;
  };

  InfoDictionary settings;
  if (toml::table* settingsTable = config[settingsKey]["settings"].as_table()) {
    // It'd be nice to use settingsTable::for_each, a lambda and
    // w/constexpr to filter supported types, but it ends up being
    // somewhat verbose due to the number of types supported by the
    // variant.
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
            fmt::format("Error parsing config file. Unsupported value type for '{}'.", key.str()));
      }
    }
  }

  return {Identifier{identifier}, settings};
}

}  // namespace hostApi::factory
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
