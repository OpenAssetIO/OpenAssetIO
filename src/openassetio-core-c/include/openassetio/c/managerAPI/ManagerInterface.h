// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include "../SimpleString.h"
#include "../namespace.h"

#ifdef __cplusplus
extern "C" {
#endif

// NOLINTNEXTLINE(modernize-use-using)
typedef struct OPENASSETIO_NS(managerAPI_ManagerInterface_t) *
    OPENASSETIO_NS(managerAPI_ManagerInterface_h);

// NOLINTNEXTLINE(modernize-use-using)
typedef struct {
  void (*dtor)(OPENASSETIO_NS(managerAPI_ManagerInterface_h));

  int (*identifier)(OPENASSETIO_NS(SimpleString) *,
                    OPENASSETIO_NS(SimpleString) *,
                    OPENASSETIO_NS(managerAPI_ManagerInterface_h));

  int (*displayName)(OPENASSETIO_NS(SimpleString) *,
                     OPENASSETIO_NS(SimpleString) *,
                     OPENASSETIO_NS(managerAPI_ManagerInterface_h));
} OPENASSETIO_NS(managerAPI_ManagerInterface_s);

#ifdef __cplusplus
}
#endif
