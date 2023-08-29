// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace hostApi {

OPENASSETIO_DECLARE_PTR(ManagerImplementationFactoryInterface)

/**
 * Manager Factories are responsible for instantiating classes that
 * derive from @fqref{managerApi.ManagerInterface} or @needsref
 * openassetio-ui.implementation.ManagerUIDelegate for use within an
 * host.
 *
 * ManagerImplementationFactoryInterface defines the abstract interface
 * that any such factory must adopt.
 *
 * Factories are expected to be lazy, so should be cheap to construct,
 * and work to discover plugins should be done in @ref identifiers /
 * @ref instantiate. Hence member functions are deliberately non-const.
 *
 * There is no guarantee that any one member function will be called
 * before another (for example, you cannot rely on @ref identifiers
 * being called before @ref instantiate).
 *
 * Implementations deriving from this class should use the provided
 * logger to report any non-critical messages. For any critical failures
 * exceptions should be thrown, and logging left up to the caller.
 */
class OPENASSETIO_CORE_EXPORT ManagerImplementationFactoryInterface {
 public:
  OPENASSETIO_ALIAS_PTR(ManagerImplementationFactoryInterface)

  /**
   * Construct an instance of this class.
   *
   * @param logger Logger object that should be used for all logging
   * by the factory. Obtainable in subclasses through @ref logger_.
   */
  explicit ManagerImplementationFactoryInterface(log::LoggerInterfacePtr logger);

  virtual ~ManagerImplementationFactoryInterface() = 0;

  /**
   * All identifiers known to the factory.
   *
   * @see @fqref{managerApi.ManagerInterface.identifier}
   * "ManagerInterface.identifier"
   */
  [[nodiscard]] virtual Identifiers identifiers() = 0;

  /**
   * Creates an instance of the \fqref{managerApi.ManagerInterface}
   * "ManagerInterface" with the specified identifier.
   *
   * @param identifier The identifier of the ManagerInterface to
   * instantiate.
   *
   * @return Newly created `ManagerInterface`.
   */
  [[nodiscard]] virtual managerApi::ManagerInterfacePtr instantiate(
      const Identifier& identifier) = 0;

 protected:
  /// Logger instance that should be used for all logging.
  // Allow violation of no protected members, since this is const and
  // within an abstract interface.
  // NOLINTNEXTLINE(misc-non-private-member-variables-in-classes)
  const log::LoggerInterfacePtr logger_;
};
}  // namespace hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
