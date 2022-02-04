# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# CMake preamble.

# * FindPython's Development.Module component was added in 3.18, and
#   pybind11 recommends 3.18.2+.
# * PROJECT_IS_TOP_LEVEL requires 3.21+
cmake_minimum_required(VERSION 3.21)

# Additional include directories for CMake utils.
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

# TODO(DF): Set CMAKE_OSX_DEPLOYMENT_TARGET when it's time to tackle OSX

# Forbid in-source builds.
if (${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    message(FATAL_ERROR
        "In-source build not allowed. Please remove generated CMakeCache.txt and CMakeFiles"
        " and re-run cmake from a separate build directory.")
endif ()

# By default, do not output "Up-to-date" messages during install. Can
# be spammy when this project is included in another via CMake's
# ExternalProject.
if (NOT DEFINED CMAKE_INSTALL_MESSAGE)
    set(CMAKE_INSTALL_MESSAGE LAZY)
endif ()


#-----------------------------------------------------------------------
# Set a default build type if none was specified

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to 'Release' as none was specified.")
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
    # Set the possible values of build type for cmake-gui, ccmake
    set_property(
        CACHE CMAKE_BUILD_TYPE
        PROPERTY STRINGS
        "Debug"
        "Release"
        "MinSizeRel"
        "RelWithDebInfo")
endif ()


#-----------------------------------------------------------------------
# IDE helpers

# Generate compile_commands.json to make it easier to work with clang
# based tools. Note: `project(...)` invisibly defines
# `CMAKE_EXPORT_COMPILE_COMMANDS` so this check must come before.
if (NOT DEFINED CMAKE_EXPORT_COMPILE_COMMANDS)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif ()

# Use folders to organise targets in IDEs via the FOLDER target
# property.
set_property(GLOBAL PROPERTY USE_FOLDERS ON)


#-----------------------------------------------------------------------
# Project metadata

project(
    OpenAssetIO
    VERSION 0.0.0
    DESCRIPTION "An open-source interoperability standard for tools and content management systems\
 used in media production."
    HOMEPAGE_URL https://github.com/TheFoundryVisionmongers/OpenAssetIO
    LANGUAGES C CXX)


#-----------------------------------------------------------------------
# Default install directory

# If the user hasn't configured cmake with an explicit
# CMAKE_INSTALL_PREFIX, then set it to safely install into ./dist, to
# help prevent the user from accidentally writing over /usr/local or
# whatever.
if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT AND PROJECT_IS_TOP_LEVEL)
    set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/dist" CACHE PATH "Installation location" FORCE)
endif ()


#-----------------------------------------------------------------------
# Compiler convenience variables

# This is a common check, so create a variable to make it more concise.
# Note: this must come after `project(...)` otherwise
# `CMAKE_CXX_COMPILER_ID` is undefined.
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(IS_GCC_OR_CLANG TRUE)
else ()
    set(IS_GCC_OR_CLANG FALSE)
endif ()


#-----------------------------------------------------------------------
# Options

# Surface `BUILD_SHARED_LIBS` as a non-hidden CMake option in CMake
# GUIs. This controls whether static or shared libs are built.
# TODO(DF): We may end up needing to support building of both shared
#   and static libs simultaneously. Also, using this means we inherit
#   the option if openassetio is used as a CMake subproject.
option(BUILD_SHARED_LIBS "Set to OFF to build static libraries" ON)

# Enable Python bindings build by default.
option(OPENASSETIO_ENABLE_PYTHON "Build Python bindings" ON)
if (OPENASSETIO_ENABLE_PYTHON)
    # Allow overriding the desired Python version.
    set(OPENASSETIO_PYTHON_VERSION "3.7" CACHE STRING "Python version")
    # By default we'll compute the correct site-packages directory
    # structure, but allow overriding.
    set(OPENASSETIO_PYTHON_SITEDIR
        ""
        CACHE STRING
        "Override default Python module install directory, relative to CMAKE_INSTALL_PREFIX")
endif ()

# Default treating compiler warnings as errors to OFF, since
# consumers of this project may use unpredictable toolchains.
# For dev/CI we should remember to switch this ON, though!
option(OPENASSETIO_WARNINGS_AS_ERRORS "Treat compiler warnings as errors" OFF)

# Enable IPO by default. For such a small project, the increased build
# resources seem worth the potential additional compiler optimisations.
option(OPENASSETIO_ENABLE_IPO
    "Enable Interprocedural Optimization, aka Link Time Optimization (LTO)" ON)

# Enable position independent code by default. This is redundant for
# shared libraries (CMake sets it automatically). Enabling this for
# static libraries allows our symbols to be linked to by downstream
# shared libraries.
option(OPENASSETIO_ENABLE_POSITION_INDEPENDENT_CODE
    "Enable position independent code for static library builds" ON)

# Disable C++11 ABI by default, as per current VFX reference
# platform(s), but allow optionally enabling.
# For reference, note that the default varies by platform, e.g.
# * CentOS 7.9.2009's GCC 6.3, `_GLIBCXX_USE_CXX11_ABI` is
#   always `0` and cannot be overridden.
# * Ubuntu 18.04's GCC 6.5, `_GLIBCXX_USE_CXX11_ABI` defaults
#   to `1`, but can be overridden.
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND
    CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 5.0)
    option(OPENASSETIO_GLIBCXX_USE_CXX11_ABI "For gcc, use the new C++11 library ABI" OFF)
endif ()

# Whether to use RPATH or RUNPATH runtime search path behavior.
if (IS_GCC_OR_CLANG)
    option(OPENASSETIO_ENABLE_NEW_DTAGS "If enabled, RUNPATH will be set, overriding RPATH" OFF)
endif ()

# Testing instrumentation.
if (IS_GCC_OR_CLANG)
    # Coverage reporting (for tests).
    option(OPENASSETIO_ENABLE_COVERAGE "Enable coverage reporting for gcc/clang" OFF)

    # Sanitizers (primarily for tests)
    option(OPENASSETIO_ENABLE_SANITIZER_ADDRESS "Enable address sanitizer" OFF)
    option(OPENASSETIO_ENABLE_SANITIZER_LEAK "Enable leak sanitizer" OFF)
    option(OPENASSETIO_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR
        "Enable undefined behavior sanitizer" OFF)
    option(OPENASSETIO_ENABLE_SANITIZER_THREAD "Enable thread sanitizer" OFF)
    option(OPENASSETIO_ENABLE_SANITIZER_MEMORY "Enable memory sanitizer" OFF)
endif ()

# Enable unit tests.
option(OPENASSETIO_ENABLE_TESTS "Create test targets" OFF)


#-----------------------------------------------------------------------
# Define default install directories, e.g. CMAKE_INSTALL_LIBDIR

include(GNUInstallDirs)


#-----------------------------------------------------------------------
# Third-party packages

include(ThirdParty)


#-----------------------------------------------------------------------
# Enable ctest testing

if (OPENASSETIO_ENABLE_TESTS)
    enable_testing()
    # Add a top-level install target, useful for tests to ensure the
    # project is installed. The special `install` target is unavailable
    # if the Unix Makefile generator (default on Linux) is used, so we
    # must shell out the build and install commands.
    add_custom_target(openassetio-install
        COMMAND "${CMAKE_COMMAND}" --build "${PROJECT_BINARY_DIR}"
        COMMAND "${CMAKE_COMMAND}" --install "${PROJECT_BINARY_DIR}")
endif()


#-----------------------------------------------------------------------
# Generate OpenAssetIOConfig.cmake et al. for bundling as a CMake lib.

# Targets exported to ${PROJECT_NAME}_EXPORTED_TARGETS will be available
# for import using find_package(OpenAssetIO).

include(CMakePackageConfigHelpers)

set(version_config_file "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake")
set(project_config_file "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake")
set(config_install_dir "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}")

# Version fetched from the top level project()
write_basic_package_version_file(
    ${version_config_file}
    # Version range supported only if generated by CMake >= 3.19.2.
    COMPATIBILITY SameMinorVersion
)

configure_package_config_file(
    cmake/Config.cmake.in
    ${project_config_file}
    INSTALL_DESTINATION ${config_install_dir}
    # TODO(DF): PATH_VARS?
)

install(
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${config_install_dir}
    NAMESPACE ${PROJECT_NAME}::
    FILE ${PROJECT_NAME}Targets.cmake
)

install(
    FILES "${project_config_file}" "${version_config_file}"
    DESTINATION "${config_install_dir}"
)

# TODO(DF): pkg-config? See OCIO.


#-----------------------------------------------------------------------
# Print a status dump

message(STATUS "Configuring ${PROJECT_NAME} ${PROJECT_VERSION}")
message(STATUS "${PROJECT_DESCRIPTION}")
message(STATUS "CMake ${CMAKE_VERSION}")
if (CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using toolchain file            = ${CMAKE_TOOLCHAIN_FILE}")
endif ()
message(STATUS "Project build dir               = ${PROJECT_BINARY_DIR}")
message(STATUS "Install prefix                  = ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Configuration types             = ${CMAKE_CONFIGURATION_TYPES}")
message(STATUS "Build type                      = ${CMAKE_BUILD_TYPE}")
message(STATUS "Build shared libs               = ${BUILD_SHARED_LIBS}")
message(STATUS "Create test targets             = ${OPENASSETIO_ENABLE_TESTS}")
message(STATUS "Warnings as errors              = ${OPENASSETIO_WARNINGS_AS_ERRORS}")
message(STATUS "Interprocedural optimization    = ${OPENASSETIO_ENABLE_IPO}")
message(STATUS "Enable PIC for static libs      = ${OPENASSETIO_ENABLE_POSITION_INDEPENDENT_CODE}")
if (IS_GCC_OR_CLANG)
    message(STATUS "New C++11 ABI for gcc           = ${OPENASSETIO_GLIBCXX_USE_CXX11_ABI}")
    message(STATUS "RUNPATH rather than RPATH       = ${OPENASSETIO_ENABLE_NEW_DTAGS}")
    message(STATUS "Coverage reports                = ${OPENASSETIO_ENABLE_COVERAGE}")
    message(STATUS "Sanitizer: Address              = ${OPENASSETIO_ENABLE_SANITIZER_ADDRESS}")
    message(STATUS "Sanitizer: Leak                 = ${OPENASSETIO_ENABLE_SANITIZER_LEAK}")
    message(STATUS "Sanitizer: Undefined behavior   = ${OPENASSETIO_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR}")
    message(STATUS "Sanitizer: Thread               = ${OPENASSETIO_ENABLE_SANITIZER_THREAD}")
    message(STATUS "Sanitizer: Memory               = ${OPENASSETIO_ENABLE_SANITIZER_MEMORY}")
endif ()
message(STATUS "Enable Python module build      = ${OPENASSETIO_ENABLE_PYTHON}")
if (OPENASSETIO_ENABLE_PYTHON)
    message(STATUS "Python relative install dir     = ${OPENASSETIO_PYTHON_SITEDIR}")
endif ()


#-----------------------------------------------------------------------
# Recurse to library targets

add_subdirectory(src)
