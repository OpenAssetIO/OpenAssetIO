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
#include <handles/InfoDictionary.hpp>

#include "StringViewReporting.hpp"

using openassetio::InfoDictionary;
namespace handles = openassetio::handles;

namespace {
/// Default storage capacity for StringView C strings.
constexpr std::size_t kStrStorageCapacity = 500;
}  // namespace

SCENARIO("InfoDictionary construction, conversion and destruction") {
  // Storage for error messages coming from C API functions.
  openassetio::Str errStorage(kStrStorageCapacity, '\0');
  OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

  GIVEN("a InfoDictionary handle constructed using the C API") {
    // TODO(DF): The only way InfoDictionary construction can error
    //  currently is `bad_alloc` (i.e. insufficient memory), which is
    //  a pain to simulate for testing.

    OPENASSETIO_NS(InfoDictionary_h) infoDictionaryHandle;
    OPENASSETIO_NS(ErrorCode)
    actualErrorCode = OPENASSETIO_NS(InfoDictionary_ctor)(&actualErrorMsg, &infoDictionaryHandle);
    CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));

    WHEN("handle is converted to a C++ instance") {
      InfoDictionary* infoDictionary = handles::InfoDictionary::toInstance(infoDictionaryHandle);

      THEN("instance can be used as a C++ InfoDictionary") {
        const openassetio::Str key = "some key";
        const openassetio::Str expectedValue = "some value";
        infoDictionary->insert({key, expectedValue});
        const openassetio::Str actualValue = std::get<openassetio::Str>(infoDictionary->at(key));
        CHECK(actualValue == expectedValue);

        AND_WHEN("dtor function is called") {
          OPENASSETIO_NS(InfoDictionary_dtor)(infoDictionaryHandle);

          THEN("InfoDictionary is deallocated") {
            // Rely on ASan to detect.
          }
        }
      }
    }
  }

  GIVEN("a InfoDictionary handle constructed using the C++ API") {
    // Convert a dynamically allocated InfoDictionary to an opaque handle.
    // Note that this models the ownership semantic of "owned by
    // client", so the client is expected to call `dtor` when done.
    OPENASSETIO_NS(InfoDictionary_h)
    infoDictionaryHandle = handles::InfoDictionary::toHandle(new InfoDictionary{});

    WHEN("dtor function is called") {
      OPENASSETIO_NS(InfoDictionary_dtor)(infoDictionaryHandle);

      THEN("InfoDictionary is deallocated") {
        // Rely on ASan to detect.
      }
    }
  }
}

/**
 * Base fixture for tests, providing a pre-populated InfoDictionary and
 * its C handle.
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

  InfoDictionary infoDictionary_{{kBoolKey, kBoolValue},
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
  infoDictionaryHandle_ = handles::InfoDictionary::toHandle(&infoDictionary_);
};

/**
 * Fixture for `typeOf` function, specialised by entry data type.
 *
 * @tparam Value Type of entry in InfoDictionary.
 */
template <typename Value>
struct TypeOfFixture;

template <>
struct TypeOfFixture<openassetio::Bool> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kBoolKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kBool);
};

template <>
struct TypeOfFixture<openassetio::Int> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kIntKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kInt);
};

template <>
struct TypeOfFixture<openassetio::Float> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kFloatKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kFloat);
};

template <>
struct TypeOfFixture<openassetio::Str> : InfoDictionaryFixture {
  inline static const openassetio::Str kKeyStr = kStrKey;
  static constexpr OPENASSETIO_NS(InfoDictionary_ValueType)
      kExpectedValueType = OPENASSETIO_NS(InfoDictionary_ValueType_kStr);
};

TEMPLATE_TEST_CASE_METHOD(TypeOfFixture,
                          "Retrieving the type of an entry in a InfoDictionary via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float,
                          openassetio::Str) {
  GIVEN("a populated C++ InfoDictionary and its C handle") {
    using Fixture = TypeOfFixture<TestType>;
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    const auto& keyStr = Fixture::kKeyStr;
    const auto& expectedValueType = Fixture::kExpectedValueType;

    // Storage for error messages coming from C API functions.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("the type of an entry is queried") {
      OPENASSETIO_NS(ConstStringView) key{keyStr.data(), keyStr.size()};
      OPENASSETIO_NS(InfoDictionary_ValueType) actualValueType;

      OPENASSETIO_NS(ErrorCode)
      actualErrorCode = OPENASSETIO_NS(InfoDictionary_typeOf)(&actualErrorMsg, &actualValueType,
                                                              infoDictionaryHandle, key);

      THEN("returned type matches expected type") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));
        CHECK(actualValueType == expectedValueType);
      }
    }
  }
}

SCENARIO("Attempting to retrieve the type of a non-existent InfoDictionary entry via C API") {
  GIVEN("a populated C++ InfoDictionary and its C handle") {
    InfoDictionaryFixture fixture{};
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
      actualErrorCode = OPENASSETIO_NS(InfoDictionary_typeOf)(&actualErrorMsg, &actualValueType,
                                                              infoDictionaryHandle, key);

      THEN("error code and message is set") {
        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOutOfRange));
        CHECK(actualErrorMsg == "Invalid key");
        CHECK(actualValueType == initialValueType);
      }
    }
  }
}

SCENARIO("Retrieve the number of entries in a InfoDictionary via C API") {
  GIVEN("a populated C++ InfoDictionary and its C handle") {
    InfoDictionaryFixture fixture{};
    auto& infoDictionary = fixture.infoDictionary_;
    const auto& infoDictionaryHandle = fixture.infoDictionaryHandle_;

    const auto& nonExistentKey = InfoDictionaryFixture::kNonExistentKeyStr;

    WHEN("the size of the map is queried") {
      const std::size_t actualSize = OPENASSETIO_NS(InfoDictionary_size)(infoDictionaryHandle);

      THEN("size is as expected") {
        const std::size_t expectedSize = infoDictionary.size();
        CHECK(actualSize == expectedSize);
      }

      AND_WHEN("an entry is added to the InfoDictionary") {
        constexpr openassetio::Int kNewValue{123};
        infoDictionary[nonExistentKey] = kNewValue;

        AND_WHEN("the size of the map is queried") {
          const std::size_t actualUpdatedSize =
              OPENASSETIO_NS(InfoDictionary_size)(infoDictionaryHandle);

          THEN("size is as expected") {
            const std::size_t expectedUpdatedSize = infoDictionary.size();

            CHECK(actualUpdatedSize == actualSize + 1);
            CHECK(actualUpdatedSize == expectedUpdatedSize);
          }
        }
      }
    }
  }
}

/**
 * Convenience macro declaring a `fn_` member pointing to a
 * InfoDictionary C API function.
 */
#define INFODICTIONARY_FN(fnName)                          \
  decltype(&OPENASSETIO_NS(InfoDictionary_##fnName)) fn_ = \
      &OPENASSETIO_NS(InfoDictionary_##fnName)  // NOLINT(bugprone-macro-parentheses)

/**
 * Fixture for a specific C API accessor function, specialised by return
 * data type.
 *
 * @tparam Value Return (out-parameter) data type of C API function.
 */
template <typename Value>
struct AccessorFixture;

/// Specialisation for getBool.
template <>
struct AccessorFixture<openassetio::Bool> : InfoDictionaryFixture {
  INFODICTIONARY_FN(getBool);
  static constexpr openassetio::Bool kInitialValue = !kBoolValue;
  static constexpr openassetio::Bool kExpectedValue = kBoolValue;
  static constexpr openassetio::Bool kAlternativeValue = !kBoolValue;
  inline static const openassetio::Str kKeyStr = kBoolKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  openassetio::Bool actualValue_ = kInitialValue;
};

/// Specialisation for getInt.
template <>
struct AccessorFixture<openassetio::Int> : InfoDictionaryFixture {
  INFODICTIONARY_FN(getInt);
  static constexpr openassetio::Int kInitialValue = 0;
  static constexpr openassetio::Int kExpectedValue = kIntValue;
  static constexpr openassetio::Int kAlternativeValue = kIntValue + 1;
  inline static const openassetio::Str kKeyStr = kIntKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kBoolKey;
  openassetio::Int actualValue_ = kInitialValue;
};

/// Specialisation for getFloat.
template <>
struct AccessorFixture<openassetio::Float> : InfoDictionaryFixture {
  INFODICTIONARY_FN(getFloat);
  static constexpr openassetio::Float kInitialValue = 0.0;
  static constexpr openassetio::Float kExpectedValue = kFloatValue;
  static constexpr openassetio::Float kAlternativeValue = kFloatValue / 2;
  inline static const openassetio::Str kKeyStr = kFloatKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  openassetio::Float actualValue_ = kInitialValue;
};

/// Specialisation for getStr.
template <>
struct AccessorFixture<openassetio::Str> : InfoDictionaryFixture {
  INFODICTIONARY_FN(getStr);
  openassetio::Str valueStorage_ = openassetio::Str(kStrStorageCapacity, '\0');
  OPENASSETIO_NS(StringView) kInitialValue{valueStorage_.size(), valueStorage_.data(), 0};
  inline static const openassetio::Str kExpectedValue = kStrValue;
  inline static const openassetio::Str kAlternativeValue = kStrValue + " alternative";
  inline static const openassetio::Str kKeyStr = kStrKey;
  inline static const openassetio::Str kWrongValueTypeKeyStr = kIntKey;
  OPENASSETIO_NS(StringView) actualValue_ = kInitialValue;
};

TEMPLATE_TEST_CASE_METHOD(AccessorFixture, "InfoDictionary accessed via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float,
                          openassetio::Str) {
  GIVEN("a populated C++ InfoDictionary and its C handle function pointer") {
    using Fixture = AccessorFixture<TestType>;
    // Map constructed with some initial data.
    auto& infoDictionary = Fixture::infoDictionary_;
    // Opaque handle to map.
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    // Function for type under test.
    const auto& fn = Fixture::fn_;

    // Storage for return (out-parameter) value.
    auto& actualValue = Fixture::actualValue_;
    // Initial value held in actualValue out-parameter before C API
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

    // Storage for error messages coming from C API functions.
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
        OPENASSETIO_NS(ConstStringView)
        key{nonExistentKeyStr.data(), nonExistentKeyStr.size()};

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
  GIVEN("a populated C++ InfoDictionary and its C handle") {
    InfoDictionaryFixture fixture{};
    // Opaque handle to map.
    const auto& infoDictionaryHandle = fixture.infoDictionaryHandle_;

    // Storage for error messages coming from C API functions.
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
        actualErrorCode = OPENASSETIO_NS(InfoDictionary_getStr)(&actualErrorMsg, &actualValue,
                                                                infoDictionaryHandle, key);

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
 * Fixture for a specific C API mutator function, specialised by return
 * data type.
 *
 * @tparam Value Input data type of C API function.
 */
template <typename Value>
struct MutatorFixture;

/// Specialisation for setBool.
template <>
struct MutatorFixture<openassetio::Bool> : InfoDictionaryFixture {
  INFODICTIONARY_FN(setBool);
  static constexpr openassetio::Bool kExpectedValue = !kBoolValue;
  inline static const openassetio::Str kKeyStr = kBoolKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

/// Specialisation for setInt.
template <>
struct MutatorFixture<openassetio::Int> : InfoDictionaryFixture {
  INFODICTIONARY_FN(setInt);
  static constexpr openassetio::Int kExpectedValue = kIntValue + 1;
  inline static const openassetio::Str kKeyStr = kIntKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kBoolKey;
};

/// Specialisation for setFloat.
template <>
struct MutatorFixture<openassetio::Float> : InfoDictionaryFixture {
  INFODICTIONARY_FN(setFloat);
  static constexpr openassetio::Float kExpectedValue = kFloatValue / 2;
  inline static const openassetio::Str kKeyStr = kFloatKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

/// Specialisation for setStr.
template <>
struct MutatorFixture<openassetio::Str> : InfoDictionaryFixture {
  INFODICTIONARY_FN(setStr);
  inline static const openassetio::Str kExpectedValue =
      InfoDictionaryFixture::kStrValue + " updated";
  inline static const openassetio::Str kKeyStr = kStrKey;
  inline static const openassetio::Str kOtherValueTypeKeyStr = kIntKey;
};

TEMPLATE_TEST_CASE_METHOD(MutatorFixture, "InfoDictionary mutated via C API", "",
                          openassetio::Bool, openassetio::Int, openassetio::Float) {
  GIVEN("a populated C++ InfoDictionary and its C handle function pointer") {
    using Fixture = MutatorFixture<TestType>;
    // Map constructed with some initial data.
    const auto& infoDictionary = Fixture::infoDictionary_;
    // Opaque handle to map.
    const auto& infoDictionaryHandle = Fixture::infoDictionaryHandle_;
    // C API function for type under test.
    const auto& fn = Fixture::fn_;

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

    // Storage for error messages coming from C API functions.
    // TODO(DF): The only exception currently possible is `bad_alloc`,
    //  which is tricky to test.
    openassetio::Str errStorage(kStrStorageCapacity, '\0');
    OPENASSETIO_NS(StringView) actualErrorMsg{errStorage.size(), errStorage.data(), 0};

    WHEN("an existing value of the same type is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode =
          fn(&actualErrorMsg, infoDictionaryHandle, {keyStr.data(), keyStr.size()}, expectedValue);

      THEN("value is updated successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(keyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("an existing value of a different type is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode =
          fn(&actualErrorMsg, infoDictionaryHandle,
             {otherValueTypeKeyStr.data(), otherValueTypeKeyStr.size()}, expectedValue);

      THEN("value is updated successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(otherValueTypeKeyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }

    WHEN("a non-existent entry is updated") {
      const OPENASSETIO_NS(ErrorCode) actualErrorCode =
          fn(&actualErrorMsg, infoDictionaryHandle,
             {nonExistentKeyStr.data(), nonExistentKeyStr.size()}, expectedValue);

      THEN("entry is created and value set successfully") {
        const TestType actualValue = std::get<TestType>(infoDictionary.at(nonExistentKeyStr));

        CHECK(actualErrorCode == OPENASSETIO_NS(ErrorCode_kOK));  // NOLINT(bugprone-infinite-loop)
        CHECK(actualValue == expectedValue);
      }
    }
  }
}
