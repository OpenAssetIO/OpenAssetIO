# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

include(DefaultTargetProperties)

#-----------------------------------------------------------------------
# Core C++ library

add_subdirectory(openassetio-core)


#-----------------------------------------------------------------------
# UI delegation C++ library

add_subdirectory(openassetio-ui)


#-----------------------------------------------------------------------
# Core C bindings library

if (OPENASSETIO_ENABLE_C)
    add_subdirectory(openassetio-core-c)
endif ()


#-----------------------------------------------------------------------
# Python bindings

if (OPENASSETIO_ENABLE_PYTHON)
    add_subdirectory(openassetio-python)
endif ()
