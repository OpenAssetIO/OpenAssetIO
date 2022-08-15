// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once
#include <string>

#include <openassetio/c/export.h>
#include <openassetio/export.h>

#include <openassetio/c/managerApi/CManagerInterface.h>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/collection.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

/**
 * ManagerInterface implementation wrapping a manager plugin defined via
 * the C API.
 */
class OPENASSETIO_CORE_C_EXPORT CManagerInterfaceAdapter : ManagerInterface {
 public:
  /**
   * Construct from a provided opaque handle and C function pointer
   * suite.
   *
   * @param handle Opaque handle to pass to suite functions.
   * @param suite Function pointer suite to call from within member
   * functions.
   */
  CManagerInterfaceAdapter(oa_managerApi_CManagerInterface_h handle,
                           oa_managerApi_CManagerInterface_s suite);

  /// Destructor that calls the C suite's `dtor` function.
  ~CManagerInterfaceAdapter() override;

  /// Wrap the C suite's `identifier` function.
  [[nodiscard]] Identifier identifier() const override;

  /// Wrap the C suite's `displayName` function.
  [[nodiscard]] Str displayName() const override;

  /// Wrap the C suite's `info` function.
  [[nodiscard]] InfoDictionary info() const override;

  /// Wrap the C suite's `initialize` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) override;

  /// Wrap the C suite's `managementPolicy` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  [[nodiscard]] trait::TraitsDatas managementPolicy(
      const trait::TraitSets& traitSets, const ContextConstPtr& context,
      const HostSessionPtr& hostSession) const override;

  /// Wrap the C suite's `isEntityReferenceString` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  [[nodiscard]] bool isEntityReferenceString(const std::string& someString,
                                             const HostSessionPtr& hostSession) const override;

  /// Wrap the C suite's `resolve` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               const ContextConstPtr& context, const HostSessionPtr& hostSession,
               const ResolveSuccessCallback& successCallback,
               const ResolveErrorCallback& errorCallback) override;

 private:
  /// Opaque handle representing a ManagerInterface for the C API.
  oa_managerApi_CManagerInterface_h handle_;
  /// Suite of C API function pointers to delegate calls to.
  oa_managerApi_CManagerInterface_s suite_;
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
