# SPDX-License-Identifier: Apache-2.0
# Copyright 2022-2024 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# C++ API test target

add_executable(openassetio-core-cpp-test-exe)
openassetio_set_default_target_properties(openassetio-core-cpp-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-core-cpp-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-core-cpp-test-exe
    PRIVATE
    main.cpp
    typedefsTest.cpp
    BatchElementErrorTest.cpp
    ContextTest.cpp
    TraitsDataTest.cpp
    deprecationsTest.cpp
    versionTest.cpp
    hostApi/ManagerTest.cpp
    managerApi/HostTest.cpp
    managerApi/HostSessionTest.cpp
    managerApi/ManagerStateBaseTest.cpp
)

target_link_libraries(
    openassetio-core-cpp-test-exe
    PRIVATE
    # Test framework.
    Catch2::Catch2
    # Mocking framework.
    trompeloeil::trompeloeil
    # Lib under test.
    openassetio-core
)


#-----------------------------------------------------------------------
# Create CTest target

# Requires: openassetio.internal.install
add_custom_target(
    openassetio.internal.core-cpp-test
    COMMAND
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-core-cpp-test-exe>"
)

openassetio_add_test_target(openassetio.internal.core-cpp-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.core-cpp-test
    openassetio.internal.install
)

#-----------------------------------------------------------------------
# Internal utils test target
#
# Target bundling and testing hidden private utils from the core
# library.

add_executable(openassetio-core-cpp-internal-test-exe)
openassetio_set_default_target_properties(openassetio-core-cpp-internal-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-core-cpp-internal-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-core-cpp-internal-test-exe
    PRIVATE
    # Implementation dependencies.
    ${PROJECT_SOURCE_DIR}/src/openassetio-core/src/utils/Regex.cpp

    # Tests.
    main.cpp
    utils/RegexTest.cpp
)

target_include_directories(
    openassetio-core-cpp-internal-test-exe
    PRIVATE
    ${PROJECT_SOURCE_DIR}/src/openassetio-core/src
)

target_link_libraries(
    openassetio-core-cpp-internal-test-exe
    PRIVATE
    openassetio-core
    # Implementation dependencies.
    fmt::fmt-header-only
    PCRE2::8BIT

    # Test dependencies.
    Catch2::Catch2
)


#-----------------------------------------------------------------------
# Create CTest target

# Requires: openassetio.internal.install
add_custom_target(
    openassetio.internal.core-cpp-internal-test
    COMMAND
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-core-cpp-internal-test-exe>"
)

openassetio_add_test_target(openassetio.internal.core-cpp-internal-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.core-cpp-internal-test
    openassetio.internal.install
)


#-----------------------------------------------------------------------
# Test resources

add_subdirectory(pluginSystem/resources/plugins)
