# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#----------------------------------------------------------------------
# Public headers

set(public_header_source_root ${CMAKE_CURRENT_LIST_DIR}/include)

# Installation location for install phase.
# TODO(DF): When CMake 3.23 is released, use FILE_SET, which allows
#   explicitly associating public headers with a target. Note that the
#   PUBLIC_HEADER target property is not useful since it flattens the
#   directory structure when installed.
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
add_library(openassetio-core)
# Set good default target options.
set_default_target_properties(openassetio-core)
# Set output artifact base filename.
set_target_properties(openassetio-core PROPERTIES OUTPUT_NAME openassetio)
# Add to the set of installable targets.
install(TARGETS openassetio-core EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

if(WIN32)
    install(TARGETS openassetio-core
        DESTINATION "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")
    install(FILES $<TARGET_PDB_FILE:openassetio-core>
        CONFIGURATIONS "Debug" "RelWithDebInfo"
        DESTINATION "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")
endif()


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(
    openassetio-core
    PRIVATE
    TraitsData.cpp
    hostAPI/Manager.cpp
    managerAPI/ManagerInterface.cpp
)

# Public header dependency.
target_include_directories(openassetio-core
    PUBLIC
    # For generated export.h header.
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>"
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
    openassetio-core
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/openassetio/export.h
    CUSTOM_CONTENT_FROM_VARIABLE define_version
)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/
)
