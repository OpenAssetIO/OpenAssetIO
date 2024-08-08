# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# Python/C++ bridge tests

add_subdirectory(bridge)


#-----------------------------------------------------------------------
# Python bindings-specific tests.

add_subdirectory(cmodule)


#-----------------------------------------------------------------------
# Tests of the core Python API.

add_subdirectory(package)


#-----------------------------------------------------------------------
# CMake Python packaging tests.

if (OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO)
    openassetio_add_pytest_target(
        openassetio.internal.pytest.cmake_package
        "Running pytest check for CMake dist-info packaging"
        "${CMAKE_CURRENT_LIST_DIR}/test_cmake.py"
        "${PROJECT_SOURCE_DIR}"
        "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
    )
    openassetio_add_test_target(openassetio.internal.pytest.cmake_package)
    openassetio_add_test_fixture_dependencies(
        openassetio.internal.pytest.cmake_package
        openassetio.internal.install
    )
    openassetio_add_test_venv_fixture_dependency(openassetio.internal.pytest.cmake_package)
    set_tests_properties(
        openassetio.internal.pytest.cmake_package
        PROPERTIES
        ENVIRONMENT OPENASSETIO_CMAKE_PACKAGE_VERSION=${PROJECT_VERSION}
    )
endif ()


#-----------------------------------------------------------------------
# Test dependencies.

# Install test-specific dependencies (e.g. pytest).
openassetio_add_python_environment_dependency(
    openassetio.internal.pytest.install-deps
    "${PROJECT_SOURCE_DIR}/src/openassetio-python/tests/requirements.txt"
)
