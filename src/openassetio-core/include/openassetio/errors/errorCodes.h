// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
#pragma once
/**
 * @file
 *
 * Defines core error code constants shared between C and C++.
 *
 * To remove any ambiguity in error codes, we want to ensure codes of
 * different error types (i.e. exceptions vs. batch element errors) do
 * not overlap.
 */

/**
 * First error code used for representing a C++ exception.
 *
 * This macro defines the starting error code that should be used for
 * exception-like errors.
 */
// NOLINTNEXTLINE(modernize-macro-to-enum)
#define OPENASSETIO_ErrorCode_BEGIN 1

/**
 * First error code used for representing a batch element error.
 *
 * Assumes a maximum of 128 exception-like error codes before these.
 */
#define OPENASSETIO_BatchErrorCode_BEGIN (OPENASSETIO_ErrorCode_BEGIN + 127)

/// Unknown error when processing a batch element.
#define OPENASSETIO_BatchErrorCode_kUnknown (OPENASSETIO_BatchErrorCode_BEGIN + 0)

/// Failure due to an entity reference not belonging to the manager.
#define OPENASSETIO_BatchErrorCode_kInvalidEntityReference (OPENASSETIO_BatchErrorCode_BEGIN + 1)

/// Failure due to an entity reference being malformed in the context of use.
#define OPENASSETIO_BatchErrorCode_kMalformedEntityReference (OPENASSETIO_BatchErrorCode_BEGIN + 2)

/// Failure due to an API method being called with an invalid @ref Context access.
#define OPENASSETIO_BatchErrorCode_kEntityAccessError (OPENASSETIO_BatchErrorCode_BEGIN + 3)

/// Entity resolution failure.
#define OPENASSETIO_BatchErrorCode_kEntityResolutionError (OPENASSETIO_BatchErrorCode_BEGIN + 4)

/// Invalid TraitsData hint given to preflight.
#define OPENASSETIO_BatchErrorCode_kInvalidPreflightHint (OPENASSETIO_BatchErrorCode_BEGIN + 5)

/// Failure due to a TraitSet being unknown to the manager
#define OPENASSETIO_BatchErrorCode_kInvalidTraitSet (OPENASSETIO_BatchErrorCode_BEGIN + 6)
