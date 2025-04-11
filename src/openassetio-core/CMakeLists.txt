# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2024 The Foundry Visionmongers Ltd

#----------------------------------------------------------------------
# Versioning

# Library ABI version
# This should be set to the major component of the last release version
# where the ABI changed.
set(_core_abi_version 1)

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
# Create core target

# Note: static vs. shared is auto-determined by CMake's built-in
# BUILD_SHARED_LIBS option.
add_library(openassetio-core)
add_library(${PROJECT_NAME}::openassetio-core ALIAS openassetio-core)
# Set good default target options.
openassetio_set_default_target_properties(openassetio-core)
# Set output artifact base filename.
set_target_properties(openassetio-core PROPERTIES OUTPUT_NAME openassetio)
# Add to the set of installable targets.
install(TARGETS openassetio-core EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

if (WIN32)
    # "TARGET_PDB_FILE is allowed only for targets with linker created
    # artifacts"
    if (BUILD_SHARED_LIBS)
        install(
            FILES $<TARGET_PDB_FILE:openassetio-core>
            TYPE BIN
            CONFIGURATIONS "Debug" "RelWithDebInfo"
        )
    endif ()
endif ()


#-----------------------------------------------------------------------
# Target dependencies

# Source file dependencies.
target_sources(
    openassetio-core
    PRIVATE
    src/Context.cpp
    src/errors/exceptionMessages.cpp
    src/hostApi/HostInterface.cpp
    src/hostApi/Manager.cpp
    src/hostApi/ManagerConveniences.cpp
    src/hostApi/ManagerFactory.cpp
    src/hostApi/ManagerImplementationFactoryInterface.cpp
    src/hostApi/EntityReferencePager.cpp
    src/log/ConsoleLogger.cpp
    src/log/LoggerInterface.cpp
    src/log/SeverityFilter.cpp
    src/managerApi/Host.cpp
    src/managerApi/HostSession.cpp
    src/managerApi/ManagerInterface.cpp
    src/managerApi/EntityReferencePagerInterface.cpp
    src/pluginSystem/CppPluginSystem.cpp
    src/pluginSystem/CppPluginSystemManagerImplementationFactory.cpp
    src/pluginSystem/CppPluginSystemManagerPlugin.cpp
    src/pluginSystem/CppPluginSystemPlugin.cpp
    src/pluginSystem/HybridPluginSystemManagerImplementationFactory.cpp
    src/trait/TraitsData.cpp
    src/utils/formatter.cpp
    src/utils/ostream.cpp
    src/utils/Regex.cpp
    src/utils/path.cpp
    src/utils/path/common.cpp
    src/utils/path/windows.cpp
    src/utils/path/windows/detail.cpp
    src/utils/path/windows/pathTypes.cpp
    src/utils/path/posix.cpp
    src/utils/path/posix/detail.cpp
    src/utils/substitute.cpp
)

# Public header dependency.
target_include_directories(openassetio-core
    PUBLIC
    # For generated export.h and version.hpp header.
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>"
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${_public_header_source_root}>"
    # Use includes from source tree for building.
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../private/include>"
    # Use includes from install tree for installed lib.
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")

target_link_libraries(
    openassetio-core
    PRIVATE
    # Header-only private dependencies:
    $<BUILD_INTERFACE:tomlplusplus::tomlplusplus>
    $<BUILD_INTERFACE:fmt::fmt-header-only>
    # (Static) private library dependencies
    ada::ada
    PCRE2::8BIT
    # For dlopen et al.
    ${CMAKE_DL_LIBS}
)

#-----------------------------------------------------------------------
# API export header

# Definition for export header, to use for versioned namespacing.
set(_define_version
    "#define OPENASSETIO_CORE_ABI_VERSION v${_core_abi_version}")

# Use CMake utility to generate the export header.
include(GenerateExportHeader)
# Note: CMake>=3.30 recommended, since it adds Clang-Tidy linter
# suppressions to the generated file.
generate_export_header(
    openassetio-core
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/openassetio/export.h
    CUSTOM_CONTENT_FROM_VARIABLE _define_version
)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/export.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/
)

#----------------------------------------------------------------------
# Version header
# Create a version.hpp with the configured version nums from template
configure_file(${PROJECT_SOURCE_DIR}/cmake/templates/include/openassetio/version.hpp.in
               ${PROJECT_BINARY_DIR}/include/openassetio/version.hpp @ONLY)

install(
    FILES ${PROJECT_BINARY_DIR}/include/openassetio/version.hpp
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/openassetio/
)

#-----------------------------------------------------------------------
# Tests

if (OPENASSETIO_ENABLE_TESTS)
    add_subdirectory(tests)
    if (OPENASSETIO_ENABLE_TEST_ABI)
        openassetio_add_abi_test_target(openassetio-core)
    endif ()
endif ()
