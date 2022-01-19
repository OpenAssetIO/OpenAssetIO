# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#----------------------------------------------------------------------
# Public headers

set(public_header_source_root ${CMAKE_CURRENT_LIST_DIR}/include)

# Installation location for install phase.
install(
    DIRECTORY
    ${public_header_source_root}/openassetio
    DESTINATION
    ${CMAKE_INSTALL_INCLUDEDIR}
)


#-----------------------------------------------------------------------
# Create core target

# Note: static vs. shared is auto-determined by CMake's built-in
# BUILD_SHARED_LIBS option.
# TODO(DF): Allow customising library name (e.g. suffix)? See OCIO.
add_library(openassetio)
# Set good default target options.
include(DefaultTargetProperties)
set_default_target_properties(openassetio)
# Add to the set of installable targets.
install(TARGETS openassetio EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

# TODO(DF): Generate and install .pdb on Windows. See OCIO.


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(openassetio
    PRIVATE
    openassetio/managerAPI/ManagerInterface.cpp)

# Public header dependency.
target_include_directories(openassetio
    PUBLIC
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${public_header_source_root}>"
    # Use includes from install tree for installed lib.
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")


#-----------------------------------------------------------------------
# API export header

# Definition for export header, to use for versioned namespacing.
# TODO(DF): It may turn out this should go in a separate header. Also
#   other projects have much more elaborate version headers. See OCIO
#   (bundles version in export header) and OTIO (uses separate header),
#   both of which include a long list of additional #defines.
set(define_version
    "#define OPENASSETIO_VERSION v${PROJECT_VERSION_MAJOR}_${PROJECT_VERSION_MINOR}")

# TODO(DF): Allow customising namespace? See OCIO.

# Use CMake utility to generate the export header.
include(GenerateExportHeader)
generate_export_header(
    openassetio
    EXPORT_FILE_NAME openassetio/export.h
    # #define that when found will configure as a static lib.
    STATIC_DEFINE ${PROJECT_NAME}_STATIC_DEFINE
    CUSTOM_CONTENT_FROM_VARIABLE define_version
)

target_include_directories(openassetio
    PRIVATE
    # For ABI header.
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>")

install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/openassetio/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/
)
