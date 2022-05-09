// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>  // For OPENASSETIO_VERSION

#include <catch2/trompeloeil.hpp>

// private headers
#include <handles.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace test {

/**
 * Mock manager API implementation that the function pointer suite (see
 * `mockManagerInterfaceSuite`) will delegate to.
 */
struct MockManagerInterfaceCApi {
  MAKE_MOCK1(dtor, void(OPENASSETIO_NS(managerAPI_ManagerInterface_h)));

  MAKE_MOCK3(identifier,
             OPENASSETIO_NS(ErrorCode)(OPENASSETIO_NS(StringView) *, OPENASSETIO_NS(StringView) *,
                                       OPENASSETIO_NS(managerAPI_ManagerInterface_h)));

  MAKE_MOCK3(displayName,
             OPENASSETIO_NS(ErrorCode)(OPENASSETIO_NS(StringView) *, OPENASSETIO_NS(StringView) *,
                                       OPENASSETIO_NS(managerAPI_ManagerInterface_h)));

  MAKE_MOCK3(info, OPENASSETIO_NS(ErrorCode)(OPENASSETIO_NS(StringView) *,
                                             OPENASSETIO_NS(InfoDictionary_h),
                                             OPENASSETIO_NS(managerAPI_ManagerInterface_h)));
};

using MockManagerInterfaceCApiHandleConverter =
    openassetio::handles::Converter<MockManagerInterfaceCApi,
                                    OPENASSETIO_NS(managerAPI_ManagerInterface_h)>;

/**
 * Get a ManagerInterface C API function pointer suite that assumes the
 * provided `handle` is a `MockCAPI` instance.
 */
inline OPENASSETIO_NS(managerAPI_ManagerInterface_s) mockManagerInterfaceSuite() {
  return {// dtor
          [](OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = MockManagerInterfaceCApiHandleConverter::toInstance(h);
            api->dtor(h);
          },
          // identifier
          [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
             OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = MockManagerInterfaceCApiHandleConverter::toInstance(h);
            return api->identifier(err, out, h);
          },
          // displayName
          [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(StringView) * out,
             OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = MockManagerInterfaceCApiHandleConverter::toInstance(h);
            return api->displayName(err, out, h);
          },
          // info
          [](OPENASSETIO_NS(StringView) * err, OPENASSETIO_NS(InfoDictionary_h) out,
             OPENASSETIO_NS(managerAPI_ManagerInterface_h) h) {
            auto *api = MockManagerInterfaceCApiHandleConverter::toInstance(h);
            return api->info(err, out, h);
          }};
}
}  // namespace test
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
