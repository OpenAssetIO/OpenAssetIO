# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# CMake preamble.

# * FindPython's Development.Module component was added in 3.18, and
#   pybind11 recommends 3.18.2+.
# * PROJECT_IS_TOP_LEVEL requires 3.21+
# * $<INSTALL_PREFIX> usage in `install(CODE` requires 3.27+
cmake_minimum_required(VERSION 3.27)

# Additional include directories for CMake utils.
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

# Minimum required for the C++17 features used.
set(CMAKE_OSX_DEPLOYMENT_TARGET 10.15)

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
    VERSION 1.0.0
    DESCRIPTION "An open-source interoperability standard for tools and content management systems\
 used in media production."
    HOMEPAGE_URL https://github.com/OpenAssetIO/OpenAssetIO
    LANGUAGES C CXX)


#-----------------------------------------------------------------------
# Default install directory

# Default install to a `dist` directory under the build directory, ready
# for use in tests and for packaging. But don't override if user has
# explicitly set CMAKE_INSTALL_PREFIX.
if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT AND PROJECT_IS_TOP_LEVEL)
    set(CMAKE_INSTALL_PREFIX "${PROJECT_BINARY_DIR}/dist" CACHE PATH "Installation location" FORCE)
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

# Enable cmake_dependent_option support
include(CMakeDependentOption)

# Surface `BUILD_SHARED_LIBS` as a non-hidden CMake option in CMake
# GUIs. This controls whether static or shared libs are built.
# TODO(DF): We may end up needing to support building of both shared
#   and static libs simultaneously. Also, using this means we inherit
#   the option if openassetio is used as a CMake subproject.
option(BUILD_SHARED_LIBS "Set to OFF to build static libraries" ON)

# Enable Python bindings build by default.
option(OPENASSETIO_ENABLE_PYTHON "Build Python bindings" ON)
if (OPENASSETIO_ENABLE_PYTHON)
    # By default we'll compute the correct site-packages directory
    # structure, but allow overriding.
    set(OPENASSETIO_PYTHON_SITEDIR
        ""
        CACHE STRING
        "Override default Python module install directory, relative to CMAKE_INSTALL_PREFIX")

    set(OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO_desc
        "Create a dist-info metadata directory alongside Python installation to provide"
        " discoverability and prevent overwrite by package managers such as pip")
    option(OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO
        "${OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO_desc}" ON)

    option(OPENASSETIO_ENABLE_PYTHON_STUBGEN "Enable Python .pyi stub file generation" ON)
endif ()

# Enable C bindings, built as a separate library that depends on the
# core C++ library.
option(OPENASSETIO_ENABLE_C "Build C bindings" OFF)

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
    # libstdc++ debug mode (e.g. container range checks).
    option(OPENASSETIO_ENABLE_GLIBCXX_DEBUG "Enable libstdc++ debug mode" OFF)
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

cmake_dependent_option(
    OPENASSETIO_ENABLE_PYTHON_TEST_VENV
    "Enable CTest fixture to create a Python environment during test runs"
    ON
    OPENASSETIO_ENABLE_TESTS
    OFF
)
cmake_dependent_option(
    OPENASSETIO_ENABLE_TEST_ABI
    "Enable ABI diff check test (Debug builds only)"
    OFF
    # Only visible if tests are enabled and this is a debug build (or is
    # a multi-config generator so has no build type).
    "OPENASSETIO_ENABLE_TESTS;NOT DEFINED CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL Debug"
    OFF
)

option(OPENASSETIO_ENABLE_SIMPLECPPMANAGER "Build the SimpleCppManager example" OFF)

# Enable clang-format formatting check.
option(OPENASSETIO_ENABLE_CLANG_FORMAT "Enable clang-format check during build" OFF)

# Enable clang-tidy static analysis tool.
option(OPENASSETIO_ENABLE_CLANG_TIDY "Enable clang-tidy analysis during build" OFF)

# Enable cpplint linter.
option(OPENASSETIO_ENABLE_CPPLINT "Enable cpplint linter during build" OFF)

# Enable cmake-lint linter.
option(OPENASSETIO_ENABLE_CMAKE_LINT "Enable cmake-lint linter during build" OFF)


#-----------------------------------------------------------------------
# Define default install directories, e.g. CMAKE_INSTALL_LIBDIR

include(GNUInstallDirs)


#-----------------------------------------------------------------------
# Third-party packages

include(ThirdParty)


#-----------------------------------------------------------------------
# Add a top-level install target, useful for tests and deployment to
# ensure the project is installed. The special `install` target is
# unavailable as a target dependency if the Unix Makefile generator
# (default on Linux) is used, so we must shell out the install.

add_custom_target(
    openassetio.internal.install
    COMMAND "${CMAKE_COMMAND}" --build "${PROJECT_BINARY_DIR}"
    --target install --parallel --config $<CONFIG>
)


#-----------------------------------------------------------------------
# Enable ctest testing

if (OPENASSETIO_ENABLE_TESTS)
    enable_testing()
    # Define test helpers.
    include(Testing)
endif ()


#-----------------------------------------------------------------------
# Enable CMake's built-in linter/static analyzer support.

include(StaticAnalyzers)
if (OPENASSETIO_ENABLE_CLANG_FORMAT)
    enable_clang_Format()
endif ()
if (OPENASSETIO_ENABLE_CLANG_TIDY)
    enable_clang_tidy()
endif ()
if (OPENASSETIO_ENABLE_CPPLINT)
    enable_cpplint()
endif ()
if (OPENASSETIO_ENABLE_CMAKE_LINT)
    enable_cmake_lint()
endif ()

#-----------------------------------------------------------------------
# Generate OpenAssetIOConfig.cmake et al. for bundling as a CMake lib.

# Targets exported to ${PROJECT_NAME}_EXPORTED_TARGETS will be available
# for import using find_package(OpenAssetIO).

include(CMakePackageConfigHelpers)

set(_version_config_file "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake")
set(_project_config_file "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake")
set(_variables_config_file "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Variables.cmake")
set(_config_install_dir "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}")

# Version fetched from the top level project()
write_basic_package_version_file(
    ${_version_config_file}
    # Version range supported only if generated by CMake >= 3.19.2.
    COMPATIBILITY SameMinorVersion
)

configure_package_config_file(
    cmake/packaging/Variables.cmake.in
    ${_variables_config_file}
    INSTALL_DESTINATION ${_config_install_dir}
)

configure_package_config_file(
    cmake/packaging/Config.cmake.in
    ${_project_config_file}
    INSTALL_DESTINATION ${_config_install_dir}
    # TODO(DF): PATH_VARS?
)

install(
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${_config_install_dir}
    NAMESPACE ${PROJECT_NAME}::
    FILE ${PROJECT_NAME}Targets.cmake
)

install(
    FILES "${_project_config_file}" "${_version_config_file}" "${_variables_config_file}"
    DESTINATION "${_config_install_dir}"
)

# TODO(DF): pkg-config? See OCIO.


#-----------------------------------------------------------------------
# Print a status dump
# cmake-lint: disable=C0301
# Above : Disable line too long as it just makes things messy here.
message(STATUS "Configuring ${PROJECT_NAME} ${PROJECT_VERSION}")
message(STATUS "${PROJECT_DESCRIPTION}")
message(STATUS "CMake ${CMAKE_VERSION}")
if (CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using toolchain file               = ${CMAKE_TOOLCHAIN_FILE}")
endif ()
message(STATUS "Project build dir                  = ${PROJECT_BINARY_DIR}")
message(STATUS "Install prefix                     = ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Configuration types                = ${CMAKE_CONFIGURATION_TYPES}")
message(STATUS "Build type                         = ${CMAKE_BUILD_TYPE}")
message(STATUS "Build shared libs                  = ${BUILD_SHARED_LIBS}")
message(STATUS "Enable Python module build         = ${OPENASSETIO_ENABLE_PYTHON}")
if (OPENASSETIO_ENABLE_PYTHON)
    message(STATUS "Python install .dist-info metadata = ${OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO}")
    message(STATUS "Python relative install dir        = ${OPENASSETIO_PYTHON_SITEDIR}")
    message(STATUS "Generate .pyi stubs                = ${OPENASSETIO_ENABLE_PYTHON_STUBGEN}")
endif ()
message(STATUS "Build SimpleCppManager             = ${OPENASSETIO_ENABLE_SIMPLECPPMANAGER}")
message(STATUS "Create test targets                = ${OPENASSETIO_ENABLE_TESTS}")
if (OPENASSETIO_ENABLE_TESTS)
    message(STATUS "Create Python venv during tests    = ${OPENASSETIO_ENABLE_PYTHON_TEST_VENV}")
    message(STATUS "Enable ABI diff check test         = ${OPENASSETIO_ENABLE_TEST_ABI}")
endif ()
message(STATUS "Warnings as errors                 = ${OPENASSETIO_WARNINGS_AS_ERRORS}")
message(STATUS "Interprocedural optimization       = ${OPENASSETIO_ENABLE_IPO}")
message(STATUS "Enable PIC for static libs         = ${OPENASSETIO_ENABLE_POSITION_INDEPENDENT_CODE}")
if (IS_GCC_OR_CLANG)
    message(STATUS "New C++11 ABI for gcc              = ${OPENASSETIO_GLIBCXX_USE_CXX11_ABI}")
    message(STATUS "RUNPATH rather than RPATH          = ${OPENASSETIO_ENABLE_NEW_DTAGS}")
    message(STATUS "Coverage reports                   = ${OPENASSETIO_ENABLE_COVERAGE}")
    message(STATUS "libstdc++ debug mode               = ${OPENASSETIO_ENABLE_GLIBCXX_DEBUG}")
    message(STATUS "Sanitizer: Address                 = ${OPENASSETIO_ENABLE_SANITIZER_ADDRESS}")
    message(STATUS "Sanitizer: Leak                    = ${OPENASSETIO_ENABLE_SANITIZER_LEAK}")
    message(STATUS "Sanitizer: Undefined behavior      = ${OPENASSETIO_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR}")
    message(STATUS "Sanitizer: Thread                  = ${OPENASSETIO_ENABLE_SANITIZER_THREAD}")
    message(STATUS "Sanitizer: Memory                  = ${OPENASSETIO_ENABLE_SANITIZER_MEMORY}")
endif ()
message(STATUS "Linter: clang-tidy                 = ${OPENASSETIO_ENABLE_CLANG_TIDY} [${OPENASSETIO_CLANGTIDY_EXE}]")
message(STATUS "Linter: cpplint                    = ${OPENASSETIO_ENABLE_CPPLINT} [${OPENASSETIO_CPPLINT_EXE}]")
message(STATUS "Linter: clang-format               = ${OPENASSETIO_ENABLE_CLANG_FORMAT} [${OPENASSETIO_CLANGFORMAT_EXE}]")
message(STATUS "Linter: cmake-lint                 = ${OPENASSETIO_ENABLE_CMAKE_LINT} [${OPENASSETIO_CMAKELINT_EXE}]")

#-----------------------------------------------------------------------
# Recurse to library targets

add_subdirectory(src)

if (OPENASSETIO_ENABLE_SIMPLECPPMANAGER)
    add_subdirectory(examples/manager/SimpleCppManager)
endif ()
