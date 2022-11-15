# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


# Core C++ API tests.
add_subdirectory(openassetio-core)

# C API bindings tests.
if (OPENASSETIO_ENABLE_C)
    add_subdirectory(openassetio-core-c)
endif ()

# Python tests.
if (OPENASSETIO_ENABLE_PYTHON)
    add_subdirectory(openassetio-python)
endif ()
