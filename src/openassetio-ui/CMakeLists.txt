# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 The Foundry Visionmongers Ltd

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
# Create ui target

# Note: static vs. shared is auto-determined by CMake's built-in
# BUILD_SHARED_LIBS option.
add_library(openassetio-ui)
add_library(${PROJECT_NAME}::openassetio-ui ALIAS openassetio-ui)
# Set good default target options.
openassetio_set_default_target_properties(openassetio-ui)
# Add to the set of installable targets.
install(TARGETS openassetio-ui EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

if (WIN32)
    # "TARGET_PDB_FILE is allowed only for targets with linker created
    # artifacts"
    if (BUILD_SHARED_LIBS)
        install(
            FILES $<TARGET_PDB_FILE:openassetio-ui>
            TYPE BIN
            CONFIGURATIONS "Debug" "RelWithDebInfo"
        )
    endif ()
endif ()


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(
    openassetio-ui
    PRIVATE
    src/ui/hostApi/UIDelegateImplementationFactoryInterface.cpp
    src/ui/hostApi/UIDelegate.cpp
    src/ui/hostApi/UIDelegateFactory.cpp
    src/ui/hostApi/UIDelegateRequestInterface.cpp
    src/ui/hostApi/UIDelegateState.cpp
    src/ui/managerApi/UIDelegateInterface.cpp
    src/ui/managerApi/UIDelegateStateInterface.cpp
    src/ui/managerApi/UIDelegateRequest.cpp
    src/ui/pluginSystem/CppPluginSystemUIDelegatePlugin.cpp
    src/ui/pluginSystem/CppPluginSystemUIDelegateImplementationFactory.cpp
    src/ui/pluginSystem/HybridPluginSystemUIDelegateImplementationFactory.cpp
)

# Public header dependency.
target_include_directories(
    openassetio-ui
    PUBLIC
    # For generated export.h header.
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>"
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${_public_header_source_root}>"
    # Use includes from install tree for installed lib.
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)

target_link_libraries(
    openassetio-ui
    PUBLIC
    # OpenAssetIO dependencies
    openassetio-core
    PRIVATE
    # Header-only private dependencies
    $<BUILD_INTERFACE:fmt::fmt-header-only>
    $<BUILD_INTERFACE:tomlplusplus::tomlplusplus>
)

#-----------------------------------------------------------------------
# API export header

# Use CMake utility to generate the export header.
include(GenerateExportHeader)
generate_export_header(
    openassetio-ui
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/openassetio/ui/export.h
    CUSTOM_CONTENT_FROM_VARIABLE _define_version
)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/ui/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/ui/
)

#-----------------------------------------------------------------------
# Tests

if (OPENASSETIO_ENABLE_TESTS)
    add_subdirectory(tests)
    if (OPENASSETIO_ENABLE_TEST_ABI)
        openassetio_add_abi_test_target(openassetio-ui)
    endif ()
endif ()
