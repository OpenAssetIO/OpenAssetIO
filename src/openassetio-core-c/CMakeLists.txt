# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#----------------------------------------------------------------------
# Public headers

set(_public_header_source_root ${CMAKE_CURRENT_LIST_DIR}/include)

# Installation location for install phase.
# TODO(DF): When CMake 3.23 is released, use FILE_SET.
install(
    DIRECTORY
    ${_public_header_source_root}/openassetio
    DESTINATION
    ${CMAKE_INSTALL_INCLUDEDIR}
)


#-----------------------------------------------------------------------
# Create core C target

# Note: static vs. shared is auto-determined by CMake's built-in
# BUILD_SHARED_LIBS option.
add_library(openassetio-core-c)
add_library(${PROJECT_NAME}::openassetio-core-c ALIAS openassetio-core-c)
# Set good default target options.
openassetio_set_default_target_properties(openassetio-core-c)
# Set output artifact base filename.
# TODO(DF): Check other OSS projects how they name C vs C++ libs
set_target_properties(openassetio-core-c PROPERTIES OUTPUT_NAME openassetio-c)
# Add to the set of installable targets.
install(TARGETS openassetio-core-c EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(
    openassetio-core-c
    PRIVATE
    src/hostApi/Manager.cpp
    src/managerApi/CManagerInterfaceAdapter.cpp
    src/InfoDictionary.cpp
)

# Public header dependency.
target_include_directories(openassetio-core-c
    PUBLIC
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${_public_header_source_root}>")

target_link_libraries(openassetio-core-c
    PUBLIC
    # Core C++ library.
    openassetio-core)


#-----------------------------------------------------------------------
# API export header

# Use CMake utility to generate the export header.
include(GenerateExportHeader)
generate_export_header(
    openassetio-core-c
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/openassetio/c/export.h
)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/c/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/c/
)


#-----------------------------------------------------------------------
# Tests

if (OPENASSETIO_ENABLE_TESTS)
    add_subdirectory(tests)
endif ()
