// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <openassetio/export.h>  // For OPENASSETIO_VERSION

#include <catch2/trompeloeil.hpp>

// private headers
#include <handles/Converter.hpp>

namespace openassetio {
inline namespace OPENASSETIO_VERSION {
namespace test {

/**
 * Mock manager API implementation that the function pointer suite (see
 * `mockManagerInterfaceSuite`) will delegate to.
 */
struct MockCManagerInterfaceImpl {
  MAKE_MOCK1(dtor, void(oa_managerAPI_CManagerInterface_h));

  MAKE_MOCK3(identifier,
             oa_ErrorCode(oa_StringView *, oa_StringView *, oa_managerAPI_CManagerInterface_h));

  MAKE_MOCK3(displayName,
             oa_ErrorCode(oa_StringView *, oa_StringView *, oa_managerAPI_CManagerInterface_h));

  MAKE_MOCK3(info, oa_ErrorCode(oa_StringView *, oa_InfoDictionary_h,
                                oa_managerAPI_CManagerInterface_h));
};

/**
 * Our simulated manager plugin's opaque handle unpacks to an instance
 * of the mock class.
 */
using MockCManagerInterfaceHandleConverter =
    openassetio::handles::Converter<MockCManagerInterfaceImpl, oa_managerAPI_CManagerInterface_h>;

/**
 * Get a ManagerInterface C API function pointer suite that assumes the
 * provided `handle` is a `MockCAPI` instance.
 */
inline oa_managerAPI_CManagerInterface_s mockManagerInterfaceSuite() {
  return {// dtor
          [](oa_managerAPI_CManagerInterface_h h) {
            MockCManagerInterfaceImpl *api = MockCManagerInterfaceHandleConverter::toInstance(h);
            api->dtor(h);
          },
          // identifier
          [](oa_StringView *err, oa_StringView *out, oa_managerAPI_CManagerInterface_h h) {
            MockCManagerInterfaceImpl *api = MockCManagerInterfaceHandleConverter::toInstance(h);
            return api->identifier(err, out, h);
          },
          // displayName
          [](oa_StringView *err, oa_StringView *out, oa_managerAPI_CManagerInterface_h h) {
            MockCManagerInterfaceImpl *api = MockCManagerInterfaceHandleConverter::toInstance(h);
            return api->displayName(err, out, h);
          },
          // info
          [](oa_StringView *err, oa_InfoDictionary_h out, oa_managerAPI_CManagerInterface_h h) {
            MockCManagerInterfaceImpl *api = MockCManagerInterfaceHandleConverter::toInstance(h);
            return api->info(err, out, h);
          }};
}
}  // namespace test
}  // namespace OPENASSETIO_VERSION
}  // namespace openassetio
