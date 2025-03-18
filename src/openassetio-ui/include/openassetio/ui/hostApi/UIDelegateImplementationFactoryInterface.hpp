// SPDX-License-Identifier: Apache-2.0
// Copyright 2025 The Foundry Visionmongers Ltd
#pragma once

#include <memory>
#include <vector>

#include <openassetio/export.h>
#include <openassetio/ui/export.h>
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(ui::managerApi, UIDelegateInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace ui::hostApi {

OPENASSETIO_DECLARE_PTR(UIDelegateImplementationFactoryInterface)

/**
 * UI Delegate Factories are responsible for instantiating classes that
 * derive from @fqref{ui.managerApi.UIDelegateInterface} for use within
 * a host.
 *
 * UIDelegateImplementationFactoryInterface defines the abstract
 * interface that any such factory must adopt.
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
// NOLINTNEXTLINE(cppcoreguidelines-special-member-functions)
class OPENASSETIO_UI_EXPORT UIDelegateImplementationFactoryInterface {
 public:
  OPENASSETIO_ALIAS_PTR(UIDelegateImplementationFactoryInterface)

  /**
   * Construct an instance of this class.
   *
   * @param logger Logger object that should be used for all logging
   * by the factory. Obtainable in subclasses through @ref logger.
   */
  explicit UIDelegateImplementationFactoryInterface(log::LoggerInterfacePtr logger);

  /// Defaulted polymorphic destructor.
  virtual ~UIDelegateImplementationFactoryInterface();

  /**
   * All identifiers known to the factory.
   *
   * @see @needsref "UIDelegateInterface.identifier"
   */
  [[nodiscard]] virtual Identifiers identifiers() = 0;

  /**
   * Creates an instance of the
   * @fqref{ui.managerApi.UIDelegateInterface} "UIDelegateInterface"
   * with the specified identifier.
   *
   * @param identifier The identifier of the UIDelegateInterface to
   * instantiate.
   *
   * @return Newly created `UIDelegateInterface`.
   */
  [[nodiscard]] virtual managerApi::UIDelegateInterfacePtr instantiate(
      const Identifier& identifier) = 0;

 protected:
  /// Get logger instance.
  [[nodiscard]] const log::LoggerInterfacePtr& logger() const;

 private:
  /// Logger instance that should be used for all logging
  log::LoggerInterfacePtr logger_;
};
}  // namespace ui::hostApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
