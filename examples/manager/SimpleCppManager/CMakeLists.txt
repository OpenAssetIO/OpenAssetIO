# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Foundry Visionmongers Ltd
cmake_minimum_required(VERSION 3.27)
# A stub C++ manager plugin useful for testing against.

#-----------------------------------------------------------------------
# Initialise project.

project(SimpleCppManager LANGUAGES CXX)

set(_target_name openassetio.example.${PROJECT_NAME})

add_library(${_target_name} MODULE)

# By default install to the root of the install prefix, so that the
# destination can be controlled precisely by the user.
set(OPENASSETIO_SIMPLECPPMANAGER_INSTALL_SUBDIR ".")
if (DEFINED OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR)
    # This variable is set either manually or because we're being
    # configured via the parent OpenAssetIO project.
    set(OPENASSETIO_SIMPLECPPMANAGER_INSTALL_SUBDIR ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR})
endif ()

install(
    TARGETS ${_target_name}
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_SIMPLECPPMANAGER_INSTALL_SUBDIR}
)

#-----------------------------------------------------------------------
# Target properties.

set_target_properties(
    ${_target_name}
    PROPERTIES

    # Ensure consistent C++17 standard.
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO

    # Ensure non-exported symbols are hidden from the host application.
    C_VISIBILITY_PRESET hidden
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES

    # Use a predictable name for the plugin binary.
    OUTPUT_NAME ${PROJECT_NAME}
    PREFIX ""
    SOVERSION ""
    VERSION ""
)

#-----------------------------------------------------------------------
# Compiler warnings.

if (MSVC)
    set(_project_warnings)
    message(AUTHOR_WARNING
        "Compiler warnings need configuring for '${CMAKE_CXX_COMPILER_ID}' compiler.")

    if (OPENASSETIO_WARNINGS_AS_ERRORS)
        set(_project_warnings ${project_warnings} /WX)
    endif ()

elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(_project_warnings -Wall -Wextra -Wpedantic)

    if (OPENASSETIO_WARNINGS_AS_ERRORS)
        set(_project_warnings ${project_warnings} -Werror)
    endif ()

else ()
    message(AUTHOR_WARNING "No compiler warnings set for '${CMAKE_CXX_COMPILER_ID}' compiler.")
endif ()

target_compile_options(${_target_name} PRIVATE ${_project_warnings})


#-----------------------------------------------------------------------
# API export header.

include(GenerateExportHeader)
generate_export_header(
    ${_target_name}
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/export.h
)


#-----------------------------------------------------------------------
# Target dependencies.

target_sources(${_target_name} PRIVATE src/${PROJECT_NAME}.cpp)

# For generated API export header.
target_include_directories(${_target_name} PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include)

if (NOT TARGET OpenAssetIO::openassetio-core)
    # We're not building as part of OpenAssetIO, so we must find it.
    find_package(OpenAssetIO REQUIRED)
endif ()

# Link to the OpenAssetIO core library.
# Note that we cannot reliably avoid baking in a dependency on the
# OpenAssetIO core library. Python (and any other process that loads
# OpenAssetIO with RTLD_LOCAL or equivalent) will not expose the
# OpenAssetIO symbols publicly. So we need to link the plugin to the
# OpenAssetIO library explicitly. This means the plugin will not load if
# the OpenAssetIO core C++ shared library is not found, e.g. if
# OpenAssetIO is statically linked into a larger third-party binary.
target_link_libraries(${_target_name} PRIVATE OpenAssetIO::openassetio-core)


#-----------------------------------------------------------------------
# Tests

if (OPENASSETIO_ENABLE_TESTS)
    if (NOT TARGET OpenAssetIO::openassetio-python-module)
        message(FATAL_ERROR
            "Testing as part of OpenAssetIO requires OPENASSETIO_ENABLE_PYTHON"
            " for pytest tests to run")
    endif ()

    enable_testing()
    add_subdirectory(tests)
endif ()

