// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include "./ns.h"

#ifdef __cplusplus
extern "C" {
#endif

// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  const size_t maxSize;
  char* buffer;
  size_t usedSize;
} OPENASSETIO_NS(SimpleString);

#ifdef __cplusplus
}
#endif
