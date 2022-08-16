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
#define OPENASSETIO_ErrorCode_BEGIN 1

/**
 * First error code used for representing a batch element error.
 *
 * Assumes a maximum of 128 exception-like error codes before these.
 */
#define OPENASSETIO_BatchErrorCode_BEGIN (OPENASSETIO_ErrorCode_BEGIN + 127)

/// Unknown error when processing a batch element.
#define OPENASSETIO_BatchErrorCode_kUnknown (OPENASSETIO_BatchErrorCode_BEGIN + 0)
