# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#-----------------------------------------------------------------------
# Python test utils static library for creating test-only bindings.

add_subdirectory(resources/_testutils)


#-----------------------------------------------------------------------
# Python bindings-specific test target.

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.pytest.cmodule
    "Running pytest for Python binding helpers"
    "${CMAKE_CURRENT_LIST_DIR}"
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)


#-----------------------------------------------------------------------
# CTest test targets

openassetio_add_test_target(openassetio.internal.pytest.cmodule)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.pytest.cmodule
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.pytest.cmodule)
# Use-after-free can result in hangs, so set a timeout.
set_tests_properties(openassetio.internal.pytest.cmodule PROPERTIES TIMEOUT 30)
