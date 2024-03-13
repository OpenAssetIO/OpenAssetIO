// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
#include <stdexcept>

[[maybe_unused]] static const int kDummy = []() -> int {
  throw std::runtime_error{"Statically thrown"};
}();
