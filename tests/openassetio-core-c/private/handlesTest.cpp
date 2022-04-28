// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd

#include <catch2/catch.hpp>

// Private headers
#include <handles.hpp>

SCENARIO("Converting to/from C++ instances and C opaque handles") {
  GIVEN("A C++ type") {
    struct StubCppType {
      std::string value_;
    };

    AND_GIVEN("a non-const instance of the C++ type") {
      StubCppType expectedCppInstance{"some string"};

      AND_GIVEN("a corresponding C handle type and a converter type") {
        using StubCppTypeHandle = struct StubCppTypeUnusedOpaqueType*;

        using Converter = openassetio::handles::Converter<StubCppType, StubCppTypeHandle>;

        WHEN("the instance is converted to a C handle") {
          StubCppTypeHandle handle = Converter::toHandle(&expectedCppInstance);

          AND_WHEN("the handle is converted back to a C++ instance") {
            StubCppType* actualCppInstance = Converter::toInstance(handle);

            THEN("the instances are the same") {
              CHECK(actualCppInstance == &expectedCppInstance);
            }
          }
        }
      }
    }

    AND_GIVEN("a const instance of the C++ type") {
      const StubCppType expectedCppInstance{"some string"};

      AND_GIVEN("a corresponding C handle type and a converter type") {
        using StubCppTypeHandle = struct StubCppTypeUnusedOpaqueType const*;

        using Converter = openassetio::handles::Converter<const StubCppType, StubCppTypeHandle>;

        WHEN("the instance is converted to a C handle") {
          StubCppTypeHandle handle = Converter::toHandle(&expectedCppInstance);

          THEN("converting back to a C++ instance will give a pointer to const") {
            STATIC_REQUIRE(
                std::is_const_v<std::remove_pointer_t<decltype(Converter::toInstance(handle))>>);
          }

          AND_WHEN("the handle is converted back to a C++ instance") {
            const StubCppType* actualCppInstance = Converter::toInstance(handle);

            THEN("the instances are the same") {
              CHECK(actualCppInstance == &expectedCppInstance);
            }
          }
        }
      }
    }
  }
}
