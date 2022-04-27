// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

#include "StringViewReporting.hpp"

SCENARIO("InfoDictionary deallocated via C API") {
  GIVEN("a heap-allocated C++ InfoDictionary and its C handle and function suite") {
    auto* infoDictionary = new openassetio::InfoDictionary{};

    // Convert InfoDictionary to opaque handle.
    auto* const infoDictionaryHandle =
        reinterpret_cast<OPENASSETIO_NS(InfoDictionary_h)>(infoDictionary);

    // InfoDictionary function pointer suite
    const auto suite = OPENASSETIO_NS(InfoDictionary_suite)();

    WHEN("suite dtor function is called") {
      suite.dtor(infoDictionaryHandle);

      THEN("InfoDictionary was deallocated") {
        // Rely on ASan to detect.
      }
    }
  }
}

/// Default storage capacity for StringView C strings.
constexpr std::size_t kStrStorageCapacity = 500;

/**
 * Base fixture for tests, providing a pre-populated InfoDictionary and its
 * C handle and function pointer suite.
 */
struct InfoDictionaryFixture {
  static constexpr openassetio::Bool kBoolValue = true;
  static constexpr openassetio::Int kIntValue = 123;
  static constexpr openassetio::Float kFloatValue = 0.456;
  inline static const openassetio::Str kStrValue = "string value";

  openassetio::InfoDictionary infoDictionary_{
      {"aBool", kBoolValue}, {"anInt", kIntValue}, {"aFloat", kFloatValue}, {"aStr", kStrValue}};

  OPENASSETIO_NS(InfoDictionary_h)
  infoDictionaryHandle_ = reinterpret_cast<OPENASSETIO_NS(InfoDictionary_h)>(&infoDictionary_);

  OPENASSETIO_NS(InfoDictionary_s) suite_ = OPENASSETIO_NS(InfoDictionary_suite)();
};

/**
 * Fixture for a specific suite function, specialised by return data
 * type.
 *
 * @tparam Value Return (out-parameter) data type of suite function.
 */
template <typename Value>
struct SuiteFnFixture;

/// Specialisation for getBool.
template <>
struct SuiteFnFixture<openassetio::Bool> : InfoDictionaryFixture {
  decltype(InfoDictionaryFixture::suite_.getBool) fn_ = InfoDictionaryFixture::suite_.getBool;
  static constexpr openassetio::Bool kInitialValue = false;
  static constexpr openassetio::Bool kExpectedValue = InfoDictionaryFixture::kBoolValue;
  static constexpr openassetio::Bool kAlternativeValue = !InfoDictionaryFixture::kBoolValue;
  inline static const openassetio::Str kKeyStr = "aBool";
  inline static const openassetio::Str kWrongValueTypeKeyStr = "anInt";
  openassetio::Bool actualValue_ = kInitialValue;
};

/// Specialisation for getInt.
template <>
struct SuiteFnFixture<openassetio::Int> : InfoDictionaryFixture {
  decltype(InfoDictionaryFixture::suite_.getInt) fn_ = InfoDictionaryFixture::suite_.getInt;
  static constexpr openassetio::Int kInitialValue = 0;
  static constexpr openassetio::Int kExpectedValue = InfoDictionaryFixture::kIntValue;
  static constexpr openassetio::Int kAlternativeValue = InfoDictionaryFixture::kIntValue + 1;
  inline static const openassetio::Str kKeyStr = "anInt";
  inline static const openassetio::Str kWrongValueTypeKeyStr = "aBool";
  openassetio::Int actualValue_ = kInitialValue;
};

/// Specialisation for getFloat.
template <>
struct SuiteFnFixture<openassetio::Float> : InfoDictionaryFixture {
  decltype(InfoDictionaryFixture::suite_.getFloat) fn_ = InfoDictionaryFixture::suite_.getFloat;
  static constexpr openassetio::Float kInitialValue = 0.0;
  static constexpr openassetio::Float kExpectedValue = InfoDictionaryFixture::kFloatValue;
  static constexpr openassetio::Float kAlternativeValue = InfoDictionaryFixture::kFloatValue / 2;
  inline static const openassetio::Str kKeyStr = "aFloat";
  inline static const openassetio::Str kWrongValueTypeKeyStr = "anInt";
  openassetio::Float actualValue_ = kInitialValue;
};

/// Specialisation for getStr.
template <>
struct SuiteFnFixture<openassetio::Str> : InfoDictionaryFixture {
  decltype(InfoDictionaryFixture::suite_.getStr) fn_ = InfoDictionaryFixture::suite_.getStr;
  openassetio::Str valueStorage_ = openassetio::Str(kStrStorageCapacity, '\0');
  OPENASSETIO_NS(StringView) kInitialValue{valueStorage_.size(), valueStorage_.data(), 0};
  inline static const openassetio::Str kExpectedValue = InfoDictionaryFixture::kStrValue;
  inline static const openassetio::Str kAlternativeValue =
      InfoDictionaryFixture::kStrValue + " alternative";
  inline static const openassetio::Str kKeyStr = "aStr";
  inline static const openassetio::Str kWrongValueTypeKeyStr = "anInt";
  OPENASSETIO_NS(StringView) actualValue_ = kInitialValue;
};

TEMPLATE_TEST_CASE_METHOD(SuiteFnFixture, "InfoDictionary accessed via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float,
                          openassetio::Str) {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite function pointer") {
    // Map constructed with some initial data.
    auto& infoDictionary = SuiteFnFixture<TestType>::infoDictionary_;
    // Opaque handle to map.
    const auto& infoDictionaryHandle = SuiteFnFixture<TestType>::infoDictionaryHandle_;
    // Suite function for type under test.
    const auto& fn = SuiteFnFixture<TestType>::fn_;

    // Storage for return (out-parameter) value.
    auto& actualValue = SuiteFnFixture<TestType>::actualValue_;
    // Initial value held in actualValue out-parameter before suite
    // function is called.
    const auto& initialValue = SuiteFnFixture<TestType>::kInitialValue;
    // Value in map at construction.
    const auto& expectedValue = SuiteFnFixture<TestType>::kExpectedValue;
    // Valid value to set in map that is not equal to expectedValue.
    const auto& alternativeValue = SuiteFnFixture<TestType>::kAlternativeValue;
    // Key in map where a value of the current type under test can be
    // found.
    const auto& keyStr = SuiteFnFixture<TestType>::kKeyStr;
    // Key in map where a value of a different type from that under test
    // can be found.
    const auto& wrongValueTypeKeyStr = SuiteFnFixture<TestType>::kWrongValueTypeKeyStr;
    // Key that doesn't exist in the map.
    const openassetio::Str nonExistentKeyStr = "nonExistent";

    // Storage for error messages coming from suite functions.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("existing value is retrieved through C API") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = fn(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("value is retrieved successfully") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("value is updated in C++ and retrieved through C API again") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};
      infoDictionary.at(keyStr) = alternativeValue;

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = fn(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("updated value is retrieved successfully") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValue == alternativeValue);
      }
    }

    WHEN("attempting to retrieve a non-existent value through C API") {
      OPENASSETIO_NS(ConstStringView) key{nonExistentKeyStr.data(), nonExistentKeyStr.size()};

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = fn(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("error code and message is set and out-param is unmodified") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOutOfRange));
        CHECK(actualErrorMsg == "Invalid key");
        CHECK(actualValue == initialValue);
      }
    }

    WHEN("attempting to retrieve an incorrect value type through C API") {
      OPENASSETIO_NS(ConstStringView)
      key{wrongValueTypeKeyStr.data(), wrongValueTypeKeyStr.size()};

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = fn(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("error code and message is set and out-param is unmodified") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kBadVariantAccess));
        CHECK(actualErrorMsg == "Invalid value type");
        CHECK(actualValue == initialValue);
      }
    }

    AND_GIVEN("error message storage capacity is very low") {
      OPENASSETIO_NS(StringView) lowCapacityErr{3, errStorage.data(), 0};

      WHEN("attempting to retrieve a non-existent value through C API") {
        OPENASSETIO_NS(ConstStringView) key{nonExistentKeyStr.data(), nonExistentKeyStr.size()};

        fn(&lowCapacityErr, &actualValue, infoDictionaryHandle, key);

        THEN("error message is truncated to fit storage capacity") {
          CHECK(lowCapacityErr == "Inv");
        }
      }

      WHEN("attempting to retrieve an incorrect value type through C API") {
        OPENASSETIO_NS(ConstStringView)
        key{wrongValueTypeKeyStr.data(), wrongValueTypeKeyStr.size()};

        fn(&lowCapacityErr, &actualValue, infoDictionaryHandle, key);

        THEN("error message is truncated to fit storage capacity") {
          CHECK(lowCapacityErr == "Inv");
        }
      }
    }
  }
}

SCENARIO("InfoDictionary string return with insufficient buffer capacity") {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite") {
    InfoDictionaryFixture fixture{};
    // Opaque handle to map.
    const auto& infoDictionaryHandle = fixture.infoDictionaryHandle_;
    // C API function suite
    const auto& suite = fixture.suite_;

    // Storage for error messages coming from suite functions.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    AND_GIVEN(
        "a StringView with insufficient storage capacity for string stored in InfoDictionary") {
      constexpr std::size_t kReducedStrStorageCapacity = 5;
      openassetio::Str valueStorage(kReducedStrStorageCapacity, '\0');
      OPENASSETIO_NS(StringView) actualValue{valueStorage.size(), valueStorage.data(), 0};

      WHEN("string is retrieved into insufficient-capacity StringView") {
        openassetio::Str keyStr = "aStr";
        OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};

        OPENASSETIO_NS(ErrorCode)
        actualErrorCode = suite.getStr(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

        THEN("truncated string is stored and error code and message is set") {
          CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kLengthError));
          CHECK(actualValue.size == actualValue.capacity);
          CHECK(actualValue == "strin");
          CHECK(actualErrorMsg == "Insufficient storage for return value");
        }
      }
    }
  }
}
