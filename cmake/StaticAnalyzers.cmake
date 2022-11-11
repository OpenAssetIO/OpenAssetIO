# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

macro(enable_clang_tidy)
    find_program(OPENASSETIO_CLANGTIDY_EXE NAMES clang-tidy clang-tidy-12)

    if (OPENASSETIO_CLANGTIDY_EXE)
        # Construct the clang-tidy command line
        set(CMAKE_CXX_CLANG_TIDY ${OPENASSETIO_CLANGTIDY_EXE})
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
    find_program(OPENASSETIO_CPPLINT_EXE cpplint)
    if (OPENASSETIO_CPPLINT_EXE)
        # Create a custom target to be added as a dependency to other
        # targets. Unfortunately the CMAKE_CXX_CPPLINT integration is
        # somewhat lacking - it won't fail the build and it won't check
        # headers. So we must roll our own target.
        add_custom_target(
            openassetio-cpplint
            COMMAND ${CMAKE_COMMAND} -E echo "Executing cpplint check..."
            COMMAND
            ${OPENASSETIO_CPPLINT_EXE}
            # The default "build/include_order" check suffers from
            # false positives since the default behaviour is to assume
            # that all `<header.h>`-like includes are C headers.
            # `standardcfirst` instead uses an allow-list of known C
            # headers. Annoyingly, this option is not supported in
            # the CPPLINT.cfg config file.
            --includeorder=standardcfirst
            --recursive
            ${PROJECT_SOURCE_DIR}/src
            ${PROJECT_SOURCE_DIR}/tests
        )

    else ()
        message(FATAL_ERROR "cpplint requested but executable not found")
    endif ()
endmacro()

macro(enable_clang_format)
    find_program(OPENASSETIO_CLANGFORMAT_EXE NAMES clang-format clang-format-12)
    if (OPENASSETIO_CLANGFORMAT_EXE)
        file(
            GLOB_RECURSE _sources
            LIST_DIRECTORIES false
            CONFIGURE_DEPENDS # Ensure we re-scan if files change.
            ${PROJECT_SOURCE_DIR}/src/*.[ch]pp
            ${PROJECT_SOURCE_DIR}/src/*.[ch]
        )

        # Create a custom target to be added as a dependency to other
        # targets.
        add_custom_target(
            openassetio-clangformat
            COMMAND ${CMAKE_COMMAND} -E echo "Executing clang-format check..."
            COMMAND
            ${OPENASSETIO_CLANGFORMAT_EXE}
            --Werror --dry-run --style=file
            ${_sources}
        )

    else ()
        message(FATAL_ERROR "clang-format requested but executable not found")
    endif ()
endmacro()
