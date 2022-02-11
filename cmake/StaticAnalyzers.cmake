# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

macro(enable_clang_tidy)
    find_program(CLANGTIDY clang-tidy)

    if (CLANGTIDY)
        # Construct the clang-tidy command line
        set(CMAKE_CXX_CLANG_TIDY ${CLANGTIDY})
        # Ignore unknown compiler flag check, otherwise e.g. GCC-only
        # compiler warning flags will cause the build to fail.
        list(APPEND CMAKE_CXX_CLANG_TIDY -extra-arg=-Wno-unknown-warning-option)

        # Set standard
        if (NOT "${CMAKE_CXX_STANDARD}" STREQUAL "")
            if ("${CMAKE_CXX_CLANG_TIDY_DRIVER_MODE}" STREQUAL "cl")
                list(APPEND CMAKE_CXX_CLANG_TIDY -extra-arg=/std:c++${CMAKE_CXX_STANDARD})
            else ()
                list(APPEND CMAKE_CXX_CLANG_TIDY -extra-arg=-std=c++${CMAKE_CXX_STANDARD})
            endif ()
        endif ()
    else ()
        message(FATAL_ERROR "clang-tidy requested but executable not found")
    endif ()
endmacro()

macro(enable_cpplint)
    find_program(CPPLINT cpplint)
    if (CPPLINT)
        # Create a custom target to be added as a dependency to other
        # targets. Unfortunately the CMAKE_CXX_CPPLINT integration is
        # somewhat lacking - it won't fail the build and it won't check
        # headers. So we must roll our own target.
        add_custom_target(
            openassetio-cpplint
            COMMENT
            "Executing cpplint"
            COMMAND
            ${CPPLINT}
            # The default "build/include_order" check suffers from
            # false positives since the default behaviour is to assume
            # that all `<header.h>`-like includes are C headers.
            # `standardcfirst` instead uses an allow-list of known C
            # headers. Annoyingly, this option is not supported in
            # the CPPLINT.cfg config file.
            --includeorder=standardcfirst
            --recursive
            ${PROJECT_SOURCE_DIR}/src
        )

    else ()
        message(FATAL_ERROR "cpplint requested but executable not found")
    endif ()
endmacro()
