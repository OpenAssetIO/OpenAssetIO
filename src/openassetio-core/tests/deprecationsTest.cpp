// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd
#include <type_traits>

#include <catch2/catch.hpp>

// Disable deprecation warning that triggers -Werror, failing the build.
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#elif defined(__GNUC__)
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#endif

#include <openassetio/TraitsData.hpp>
#include <openassetio/trait/TraitsData.hpp>

#include <openassetio/BatchElementError.hpp>
#include <openassetio/errors/BatchElementError.hpp>

// Tests for deprecated functionality.
// All cases must have links to the relevant GitHub issues.

// https://github.com/OpenAssetIO/OpenAssetIO/issues/1127
SCENARIO("TraitsData still accessible in top level namespace") {
  STATIC_REQUIRE(std::is_same_v<openassetio::TraitsData, openassetio::trait::TraitsData>);
}

// https://github.com/OpenAssetIO/OpenAssetIO/issues/1071
// https://github.com/OpenAssetIO/OpenAssetIO/issues/1073
SCENARIO("BatchElementError and exceptions still accessible in top level namespace") {
  STATIC_REQUIRE(
      std::is_same_v<openassetio::BatchElementError, openassetio::errors::BatchElementError>);
}
SCENARIO("BatchElementExceptions still accessible in top level namespace") {
  const openassetio::BatchElementError anError{
      openassetio::BatchElementError::ErrorCode::kEntityAccessError, "msg"};
  const openassetio::BatchElementException anException{0, anError};
  CHECK(anException.what() == std::string{"msg"});

  STATIC_REQUIRE(std::is_base_of_v<openassetio::errors::BatchElementException,
                                   openassetio::BatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::UnknownBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::InvalidEntityReferenceBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::MalformedEntityReferenceBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::EntityAccessErrorBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::EntityResolutionErrorBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::InvalidPreflightHintBatchElementException>);
  STATIC_REQUIRE(std::is_base_of_v<openassetio::BatchElementException,
                                   openassetio::InvalidTraitSetBatchElementException>);
}
