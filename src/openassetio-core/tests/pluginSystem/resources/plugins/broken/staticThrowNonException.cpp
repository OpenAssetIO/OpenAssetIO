// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd

[[maybe_unused]] static const int kDummy = []() -> int {
  throw 123;  // NOLINT
}();
