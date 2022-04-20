// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include <openassetio/c/InfoDictionary.h>
#include <openassetio/c/StringView.h>
#include <openassetio/c/errors.h>
#include <openassetio/c/namespace.h>

#include <catch2/catch.hpp>

#include <openassetio/InfoDictionary.hpp>
#include <openassetio/typedefs.hpp>

// Private headers.
#include <handles.hpp>

#include "StringViewReporting.hpp"

namespace {
using HandleConverter =
    openassetio::handles::Converter<openassetio::InfoDictionary, OPENASSETIO_NS(InfoDictionary_h)>;

/// Default storage capacity for StringView C strings.
constexpr std::size_t kStrStorageCapacity = 500;
}  // namespace

SCENARIO("InfoDictionary construction, conversion and destruction") {
  // Storage for error messages coming from suite functions.
  openassetio::Str errStorage(kStrStorageCapacity, '\0');
  OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

  GIVEN("InfoDictionary C function suite") {
    // InfoDictionary function pointer suite
    const auto suite = OPENASSETIO_NS(InfoDictionary_suite)();

    WHEN("a InfoDictionary handle is constructed using the C API") {
      // TODO(DF): The only way InfoDictionary construction can error
      //  currently is `bad_alloc` (i.e. insufficient memory), which is
      //  a pain to simulate for testing.

      OPENASSETIO_NS(InfoDictionary_h) infoDictionaryHandle;
      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = suite.ctor(&actualErrorMsg, &infoDictionaryHandle);

      THEN("the returned handle can be converted and used as a C++ InfoDictionary") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));

        openassetio::InfoDictionary* infoDictionary =
            HandleConverter::toInstance(infoDictionaryHandle);

        const openassetio::Str key = "some key";
        const openassetio::Str expectedValue = "some value";
        infoDictionary->insert({key, expectedValue});
        const openassetio::Str actualValue = std::get<openassetio::Str>(infoDictionary->at(key));
        CHECK(actualValue == expectedValue);

        AND_WHEN("suite dtor function is called") {
          suite.dtor(infoDictionaryHandle);

          THEN("InfoDictionary was deallocated") {
            // Rely on ASan to detect.
          }
        }
      }
    }

    WHEN("a InfoDictionary handle is constructed using the C++ API") {
      // Convert a dynamically allocated InfoDictionary to an opaque handle.
      // Note that this models the ownership semantic of "owned by
      // client", so the client is expected to call `dtor` when done.
      OPENASSETIO_NS(InfoDictionary_h)
      infoDictionaryHandle = HandleConverter::toHandle(new openassetio::InfoDictionary{});

      AND_WHEN("suite dtor function is called") {
        suite.dtor(infoDictionaryHandle);

        THEN("InfoDictionary was deallocated") {
          // Rely on ASan to detect.
        }
      }
    }
  }
}

/**
 * Base fixture for tests, providing a pre-populated InfoDictionary and its
 * C handle and function pointer suite.
 */
struct InfoDictionaryFixture {
  inline static const openassetio::Str kBoolKey = "aBool";
  static constexpr openassetio::Bool kBoolValue = true;
  inline static const openassetio::Str kIntKey = "anInt";
  static constexpr openassetio::Int kIntValue = 123;
  inline static const openassetio::Str kFloatKey = "aFloat";
  static constexpr openassetio::Float kFloatValue = 0.456;
  inline static const openassetio::Str kStrKey = "aStr";
  inline static const openassetio::Str kStrValue = "string value";

  openassetio::InfoDictionary infoDictionary_{{kBoolKey, kBoolValue},
                                              {kIntKey, kIntValue},
                                              {kFloatKey, kFloatValue},
                                              {kStrKey, kStrValue}};

  // Key that doesn't exist in the map.
  static inline const openassetio::Str kNonExistentKeyStr = "nonExistent";

  // Note that this models the ownership semantic of "owned by service",
  // i.e. the C client should not call `dtor` to destroy the instance.
  // We do not expect this to be the norm for InfoDictionary, it's just
  // convenient for these tests.
  OPENASSETIO_NS(InfoDictionary_h)
  infoDictionaryHandle_ = HandleConverter::toHandle(&infoDictionary_);

  OPENASSETIO_NS(InfoDictionary_s) suite_ = OPENASSETIO_NS(InfoDictionary_suite)();
};

/**
 * Fixture for `typeOf` function, specialised by entry data type.
 *
 * @tparam Value Type of entry in InfoDictionary.
 */
template <typename Value>
struct SuiteTypeOfFixture;

template <>
struct SuiteTypeOfFixture<openassetio::Bool> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kBoolKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kBool);
};

template <>
struct SuiteTypeOfFixture<openassetio::Int> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kIntKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kInt);
};

template <>
struct SuiteTypeOfFixture<openassetio::Float> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kFloatKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kFloat);
};

template <>
struct SuiteTypeOfFixture<openassetio::Str> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kStrKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kStr);
};

TEMPLATE_TEST_CASE_METHOD(SuiteTypeOfFixture,
                          "Retrieving the type of an entry in a InfoDictionary via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float,
                          openassetio::Str) {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite") {
    using Fixture = SuiteTypeOfFixture<TestType>;
    const auto& suite = Fixture::suite_;
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    const auto& keyStr = Fixture::kKeyStr;
    const auto& expectedValueType = Fixture::kExpectedValueType;

    // Storage for error messages coming from suite functions.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("the type of an entry is queried") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};
      OPENASSETIO_NS(InfoDictionary_ValueType) actualValueType;

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = suite.typeOf(&actualErrorMsg, &actualValueType, infoDictionaryHandle, key);

      THEN("returned type matches expected type") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValueType == expectedValueType);
      }
    }
  }
}

SCENARIO("Attempting to retrieve the type of a non-existent InfoDictionary entry via C API") {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite") {
    InfoDictionaryFixture fixture{};
    const auto& suite = fixture.suite_;
    const auto& infoDictionaryHandle = fixture.infoDictionaryHandle_;

    WHEN("the type of a non-existent entry is queried") {
      // Key to non-existent entry.
      const auto& nonExistentKey = InfoDictionaryFixture::kNonExistentKeyStr;
      OPENASSETIO_NS(ConstStringView) key{nonExistentKey.data(), nonExistentKey.size()};
      // Storage for error message.
      openassetio::Str errStorage(kStrStorageCapacity, '\0');
      OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};
      // Initial value of storage for return value.
      const OPENASSETIO_NS(InfoDictionary_ValueType) initialValueType{};
      // Storage for return value.
      OPENASSETIO_NS(InfoDictionary_ValueType) actualValueType = initialValueType;

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = suite.typeOf(&actualErrorMsg, &actualValueType, infoDictionaryHandle, key);

      THEN("error code and message is set") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOutOfRange));
        CHECK(actualErrorMsg == "Invalid key");
        CHECK(actualValueType == initialValueType);
      }
    }
  }
}

/**
 * Fixture for a specific suite accessor function, specialised by return
 * data type.
 *
 * @tparam Value Return (out-parameter) data type of suite function.
 */
template <typename Value>
struct SuiteAccessorFixture;

/// Specialisation for getBool.
template <>
struct SuiteAccessorFixture<openassetio::Bool> : InfoDictionaryFixture {
  decltype(suite_.getBool) getter_ = suite_.getBool;
  static constexpr openassetio::Bool kInitialValue = !kBoolValue;
  static constexpr openassetio::Bool kExpectedValue = kBoolValue;
  static constexpr openassetio::Bool kAlternativeValue = !kBoolValue;
  inline static const openassetio::Str kKeyStr = kBoolKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  openassetio::Bool actualValue_ = kInitialValue;
};

/// Specialisation for getInt.
template <>
struct SuiteAccessorFixture<openassetio::Int> : InfoDictionaryFixture {
  decltype(suite_.getInt) getter_ = suite_.getInt;
  static constexpr openassetio::Int kInitialValue = 0;
  static constexpr openassetio::Int kExpectedValue = kIntValue;
  static constexpr openassetio::Int kAlternativeValue = kIntValue + 1;
  inline static const openassetio::Str kKeyStr = kIntKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kBoolKey;
  openassetio::Int actualValue_ = kInitialValue;
};

/// Specialisation for getFloat.
template <>
struct SuiteAccessorFixture<openassetio::Float> : InfoDictionaryFixture {
  decltype(suite_.getFloat) getter_ = suite_.getFloat;
  static constexpr openassetio::Float kInitialValue = 0.0;
  static constexpr openassetio::Float kExpectedValue = kFloatValue;
  static constexpr openassetio::Float kAlternativeValue = kFloatValue / 2;
  inline static const openassetio::Str kKeyStr = kFloatKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  openassetio::Float actualValue_ = kInitialValue;
};

/// Specialisation for getStr.
template <>
struct SuiteAccessorFixture<openassetio::Str> : InfoDictionaryFixture {
  decltype(suite_.getStr) getter_ = suite_.getStr;
  openassetio::Str valueStorage_ = openassetio::Str(kStrStorageCapacity, '\0');
  OPENASSETIO_NS(StringView) kInitialValue{valueStorage_.size(), valueStorage_.data(), 0};
  inline static const openassetio::Str kExpectedValue = kStrValue;
  inline static const openassetio::Str kAlternativeValue = kStrValue + " alternative";
  inline static const openassetio::Str kKeyStr = kStrKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  OPENASSETIO_NS(StringView) actualValue_ = kInitialValue;
};

TEMPLATE_TEST_CASE_METHOD(SuiteAccessorFixture, "InfoDictionary accessed via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float,
                          openassetio::Str) {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite function pointer") {
    using Fixture = SuiteAccessorFixture<TestType>;
    // Map constructed with some initial data.
    auto& infoDictionary = Fixture::infoDictionary_;
    // Opaque handle to map.
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    // Suite function for type under test.
    const auto& getter = Fixture::getter_;

    // Storage for return (out-parameter) value.
    auto& actualValue = Fixture::actualValue_;
    // Initial value held in actualValue out-parameter before suite
    // function is called.
    const auto& initialValue = Fixture::kInitialValue;
    // Value in map at construction.
    const auto& expectedValue = Fixture::kExpectedValue;
    // Valid value to set in map that is not equal to expectedValue.
    const auto& alternativeValue = Fixture::kAlternativeValue;
    // Key in map where a value of the current type under test can be
    // found.
    const auto& keyStr = Fixture::kKeyStr;
    // Key in map where a value of a different type from that under test
    // can be found.
    const auto& wrongValueTypeKeyStr = Fixture::kWrongValueTypeKeyStr;
    // Key that doesn't exist in the map.
    const openassetio::Str& nonExistentKeyStr = Fixture::kNonExistentKeyStr;

    // Storage for error messages coming from suite functions.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("existing value is retrieved through C API") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = getter(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("value is retrieved successfully") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("value is updated in C++ and retrieved through C API again") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};
      infoDictionary.at(keyStr) = alternativeValue;

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = getter(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("updated value is retrieved successfully") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValue == alternativeValue);
      }
    }

    WHEN("attempting to retrieve a non-existent value through C API") {
      OPENASSETIO_NS(ConstStringView) key{nonExistentKeyStr.data(), nonExistentKeyStr.size()};

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = getter(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

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
      actualErrorCode = getter(&actualErrorMsg, &actualValue, infoDictionaryHandle, key);

      THEN("error code and message is set and out-param is unmodified") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kBadVariantAccess));
        CHECK(actualErrorMsg == "Invalid value type");
        CHECK(actualValue == initialValue);
      }
    }

    AND_GIVEN("error message storage capacity is very low") {
      OPENASSETIO_NS(StringView) lowCapacityErr{3, errStorage.data(), 0};

      WHEN("attempting to retrieve a non-existent value through C API") {
        OPENASSETIO_NS(ConstStringView)
        key{nonExistentKeyStr.data(), nonExistentKeyStr.size()};

        getter(&lowCapacityErr, &actualValue, infoDictionaryHandle, key);

        THEN("error message is truncated to fit storage capacity") {
          CHECK(lowCapacityErr == "Inv");
        }
      }

      WHEN("attempting to retrieve an incorrect value type through C API") {
        OPENASSETIO_NS(ConstStringView)
        key{wrongValueTypeKeyStr.data(), wrongValueTypeKeyStr.size()};

        getter(&lowCapacityErr, &actualValue, infoDictionaryHandle, key);

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
        "a StringView with insufficient storage capacity for string stored in "
        "InfoDictionary") {
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

/**
 * Fixture for a specific suite mutator function, specialised by return
 * data type.
 *
 * @tparam Value Input data type of suite function.
 */
template <typename Value>
struct SuiteMutatorFixture;

/// Specialisation for setBool.
template <>
struct SuiteMutatorFixture<openassetio::Bool> : InfoDictionaryFixture {
  decltype(suite_.setBool) setter_ = suite_.setBool;
  static constexpr openassetio::Bool kExpectedValue = !kBoolValue;
  inline static const openassetio::Str kKeyStr = kBoolKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

/// Specialisation for setInt.
template <>
struct SuiteMutatorFixture<openassetio::Int> : InfoDictionaryFixture {
  decltype(suite_.setInt) setter_ = suite_.setInt;
  static constexpr openassetio::Int kExpectedValue = kIntValue + 1;
  inline static const openassetio::Str kKeyStr = kIntKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kBoolKey;
};

/// Specialisation for setFloat.
template <>
struct SuiteMutatorFixture<openassetio::Float> : InfoDictionaryFixture {
  decltype(suite_.setFloat) setter_ = suite_.setFloat;
  static constexpr openassetio::Float kExpectedValue = kFloatValue / 2;
  inline static const openassetio::Str kKeyStr = kFloatKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

/// Specialisation for setStr.
template <>
struct SuiteMutatorFixture<openassetio::Str> : InfoDictionaryFixture {
  decltype(suite_.setStr) setter_ = InfoDictionaryFixture::suite_.setStr;
  inline static const openassetio::Str kExpectedValue =
      InfoDictionaryFixture::kStrValue + " updated";
  inline static const openassetio::Str kKeyStr = kStrKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

TEMPLATE_TEST_CASE_METHOD(SuiteMutatorFixture, "InfoDictionary mutated via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float) {
  GIVEN("a populated C++ InfoDictionary and its C handle and suite function pointer") {
    using Fixture = SuiteMutatorFixture<TestType>;
    // Map constructed with some initial data.
    const auto& infoDictionary = Fixture::infoDictionary_;
    // Opaque handle to map.
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    // Suite function for type under test.
    const auto& setter = Fixture::setter_;

    // Valid value to set in map that is not equal to initial value.
    const auto& expectedValue = Fixture::kExpectedValue;
    // Key in map where a value of the current type under test can be
    // found.
    const auto& keyStr = Fixture::kKeyStr;
    // Key in map where a value of a different type from that under test
    // can be found.
    const auto& otherValueTypeKeyStr = Fixture::kOtherValueTypeKeyStr;
    // Key that doesn't exist in the map.
    const openassetio::Str& nonExistentKeyStr = Fixture::kNonExistentKeyStr;

    // Storage for error messages coming from suite functions.
    // TODO(DF): The only exception currently possible is `bad_alloc`,
    //  which is tricky to test.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("an existing value of the same type is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode = setter(
          &actualErrorMsg, infoDictionaryHandle, {keyStr.data(), keyStr.size()}, expectedValue);

      THEN("value is updated successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(keyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("an existing value of a different type is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode =
          setter(&actualErrorMsg, infoDictionaryHandle,
                 {otherValueTypeKeyStr.data(), otherValueTypeKeyStr.size()}, expectedValue);

      THEN("value is updated successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(otherValueTypeKeyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("a non-existent entry is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode =
          setter(&actualErrorMsg, infoDictionaryHandle,
                 {nonExistentKeyStr.data(), nonExistentKeyStr.size()}, expectedValue);

      THEN("entry is created and value set successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(nonExistentKeyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }
  }
}
