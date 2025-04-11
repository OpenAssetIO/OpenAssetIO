# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# Test resources

add_subdirectory(pluginSystem/resources/plugins)

#-----------------------------------------------------------------------
# C++ UI delegation API test target

add_executable(openassetio-ui-cpp-test-exe)
openassetio_set_default_target_properties(openassetio-ui-cpp-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-ui-cpp-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-ui-cpp-test-exe
    PRIVATE
    main.cpp
    UIDelegateRequestStateTest.cpp
    hostApi/UIDelegateTest.cpp
)

target_link_libraries(
    openassetio-ui-cpp-test-exe
    PRIVATE
    # Test framework.
    Catch2::Catch2
    # Mocking framework.
    trompeloeil::trompeloeil
    # Lib under test.
    openassetio-ui
)


#-----------------------------------------------------------------------
# Create CTest target

# Requires: openassetio.internal.install
add_custom_target(
    openassetio.internal.core-ui-test
    COMMAND
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-ui-cpp-test-exe>"
)

openassetio_add_test_target(openassetio.internal.core-ui-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.core-ui-test
    openassetio.internal.install
)
