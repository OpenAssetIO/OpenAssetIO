// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#include <openassetio/ui/hostApi/UIDelegateFactory.hpp>

#include <cstdlib>
#include <memory>
#include <string_view>
#include <utility>

#include <openassetio/export.h>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/private/hostApi/factory.hpp>
#include <openassetio/typedefs.hpp>
#include <openassetio/ui/hostApi/UIDelegate.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

namespace factory = openassetio::hostApi::factory;
using HostSession = openassetio::managerApi::HostSession;
using HostSessionPtr = openassetio::managerApi::HostSessionPtr;
using Host = openassetio::managerApi::Host;

const Str UIDelegateFactory::kDefaultUIDelegateConfigEnvVarName{factory::kDefaultConfigEnvVarName};

UIDelegateFactoryPtr UIDelegateFactory::make(
    HostInterfacePtr hostInterface,
    UIDelegateImplementationFactoryInterfacePtr uiDelegateImplementationFactory,
    log::LoggerInterfacePtr logger) {
  return std::make_shared<UIDelegateFactory>(UIDelegateFactory{
      std::move(hostInterface), std::move(uiDelegateImplementationFactory), std::move(logger)});
}

UIDelegateFactory::UIDelegateFactory(
    HostInterfacePtr hostInterface,
    UIDelegateImplementationFactoryInterfacePtr uiDelegateImplementationFactory,
    log::LoggerInterfacePtr logger)
    : hostInterface_{std::move(hostInterface)},
      uiDelegateImplementationFactory_{std::move(uiDelegateImplementationFactory)},
      logger_{std::move(logger)} {}

Identifiers UIDelegateFactory::identifiers() const {
  return uiDelegateImplementationFactory_->identifiers();
}

UIDelegateFactory::UIDelegateDetails UIDelegateFactory::availableUIDelegates() const {
  return factory::queryBasicDetails<UIDelegateDetail>(uiDelegateImplementationFactory_);
}

UIDelegatePtr UIDelegateFactory::createUIDelegate(const Identifier& identifier) const {
  return createUIDelegateForInterface(identifier, hostInterface_, uiDelegateImplementationFactory_,
                                      logger_);
}

UIDelegatePtr UIDelegateFactory::createUIDelegateForInterface(
    const Identifier& identifier, const HostInterfacePtr& hostInterface,
    const UIDelegateImplementationFactoryInterfacePtr& uiDelegateImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  return UIDelegate::make(uiDelegateImplementationFactory->instantiate(identifier),
                          HostSession::make(Host::make(hostInterface), logger));
}

UIDelegatePtr UIDelegateFactory::defaultUIDelegateForInterface(
    const HostInterfacePtr& hostInterface,
    const UIDelegateImplementationFactoryInterfacePtr& uiDelegateImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  if (const char* configPath =
          factory::configPathFromEnvVar(logger, kDefaultUIDelegateConfigEnvVarName)) {
    return defaultUIDelegateForInterface(configPath, hostInterface,
                                         uiDelegateImplementationFactory, logger);
  }
  return nullptr;
}

UIDelegatePtr UIDelegateFactory::defaultUIDelegateForInterface(
    const std::string_view configPath, const HostInterfacePtr& hostInterface,
    const UIDelegateImplementationFactoryInterfacePtr& uiDelegateImplementationFactory,
    const log::LoggerInterfacePtr& logger) {
  const auto& [identifier, settings] =
      factory::identifierAndSettingsFromConfigFile(logger, configPath, "ui");

  const HostSessionPtr hostSession = HostSession::make(Host::make(hostInterface), logger);

  const UIDelegatePtr uiDelegate = UIDelegate::make(
      uiDelegateImplementationFactory->instantiate(Identifier(identifier)), hostSession);

  uiDelegate->initialize(settings);
  return uiDelegate;
}
}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
