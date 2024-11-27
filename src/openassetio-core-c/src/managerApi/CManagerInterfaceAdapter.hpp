// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2024 The Foundry Visionmongers Ltd
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

  CManagerInterfaceAdapter(const CManagerInterfaceAdapter&) = delete;
  CManagerInterfaceAdapter(CManagerInterfaceAdapter&&) noexcept = default;
  CManagerInterfaceAdapter& operator=(const CManagerInterfaceAdapter&) = delete;
  CManagerInterfaceAdapter& operator=(CManagerInterfaceAdapter&&) noexcept = default;

  /// Wrap the C suite's `identifier` function.
  [[nodiscard]] Identifier identifier() const override;

  /// Wrap the C suite's `displayName` function.
  [[nodiscard]] Str displayName() const override;

  /// Wrap the C suite's `info` function.
  [[nodiscard]] InfoDictionary info() override;

  // Wrap the C suite's `hasCapability` function.
  [[nodiscard]] bool hasCapability(Capability capability) override;

  /// Wrap the C suite's `initialize` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void initialize(InfoDictionary managerSettings, const HostSessionPtr& hostSession) override;

  /// Wrap the C suite's `managementPolicy` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  [[nodiscard]] trait::TraitsDatas managementPolicy(const trait::TraitSets& traitSets,
                                                    access::PolicyAccess policyAccess,
                                                    const ContextConstPtr& context,
                                                    const HostSessionPtr& hostSession) override;

  /// Wrap the C suite's `isEntityReferenceString` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  [[nodiscard]] bool isEntityReferenceString(const Str& someString,
                                             const HostSessionPtr& hostSession) override;

  /// Wrap the C suite's `entityExists` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void entityExists(const EntityReferences& entityReferences, const ContextConstPtr& context,
                    const HostSessionPtr& hostSession,
                    const ExistsSuccessCallback& successCallback,
                    const BatchElementErrorCallback& errorCallback) override;

  /// Wrap the C suite's `resolve` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void resolve(const EntityReferences& entityReferences, const trait::TraitSet& traitSet,
               access::ResolveAccess resolveAccess, const ContextConstPtr& context,
               const HostSessionPtr& hostSession, const ResolveSuccessCallback& successCallback,
               const BatchElementErrorCallback& errorCallback) override;

  /// Wrap the C suite's `preflight` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void preflight(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsDatas,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const HostSessionPtr& hostSession,
                 const PreflightSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override;

  /// Wrap the C suite's `register` function.
  /// @todo Implement C API. Currently throws `runtime_error`.
  void register_(const EntityReferences& entityReferences, const trait::TraitsDatas& traitsDatas,
                 access::PublishingAccess publishingAccess, const ContextConstPtr& context,
                 const HostSessionPtr& hostSession, const RegisterSuccessCallback& successCallback,
                 const BatchElementErrorCallback& errorCallback) override;

 private:
  /// Opaque handle representing a ManagerInterface for the C API.
  oa_managerApi_CManagerInterface_h handle_;
  /// Suite of C API function pointers to delegate calls to.
  oa_managerApi_CManagerInterface_s suite_;
};

}  // namespace managerApi
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
