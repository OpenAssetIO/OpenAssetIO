# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2024 The Foundry Visionmongers Ltd

#----------------------------------------------------------------------
# Public headers

set(_public_header_source_root ${CMAKE_CURRENT_LIST_DIR}/include)

# Installation location for install phase.
install(
    DIRECTORY
    ${_public_header_source_root}/openassetio
    DESTINATION
    ${CMAKE_INSTALL_INCLUDEDIR}
)


#-----------------------------------------------------------------------
# Create C++ Python bridge target

# Note: static vs. shared is auto-determined by CMake's built-in
# BUILD_SHARED_LIBS option.
add_library(openassetio-python-bridge)
add_library(${PROJECT_NAME}::openassetio-python-bridge ALIAS openassetio-python-bridge)
# Set good default target options.
openassetio_set_default_target_properties(openassetio-python-bridge)
# Set output artifact base filename.
set_target_properties(openassetio-python-bridge PROPERTIES OUTPUT_NAME openassetio-python)
# Add to the set of installable targets.
install(TARGETS openassetio-python-bridge EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

if (WIN32 AND OPENASSETIO_ENABLE_PYTHON)
    # "TARGET_PDB_FILE is allowed only for targets with linker created
    # artifacts"
    if (BUILD_SHARED_LIBS)
        install(
            FILES $<TARGET_PDB_FILE:openassetio-python-bridge>
            TYPE BIN
            CONFIGURATIONS "Debug" "RelWithDebInfo"
        )
    endif ()
endif ()


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(
    openassetio-python-bridge
    PRIVATE
    src/python/hostApi.cpp
    src/python/converter.cpp
    src/python/ui/hostApi.cpp
)

# Public header dependency.
target_include_directories(openassetio-python-bridge
    PUBLIC
    # Common helpers only available at build time.
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../private/include>"
    # For generated export.h header.
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>"
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${_public_header_source_root}>"
    # Use includes from install tree for installed lib.
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")

# Library dependencies.
target_link_libraries(openassetio-python-bridge
    PUBLIC
    openassetio-core
    openassetio-ui
    PRIVATE
    # pybind11 is not needed by consumers in order to use this target,
    # so we don't want it listed as a required dependency in
    # OpenAssetIOConfig.cmake et al.
    $<BUILD_INTERFACE:pybind11::module>)


#-----------------------------------------------------------------------
# API export header

# Use CMake utility to generate the export header.
include(GenerateExportHeader)
generate_export_header(
    openassetio-python-bridge
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/openassetio/python/export.h
)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/python/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/python/
)
