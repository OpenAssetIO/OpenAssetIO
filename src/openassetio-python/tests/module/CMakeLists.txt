# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#-----------------------------------------------------------------------
# Python test module target for creating test-only bindings.

add_subdirectory(resources/_openassetio_test)


#-----------------------------------------------------------------------
# Python bindings-specific test target.

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.pytest.module
    "Running pytest for Python binding helpers"
    "${CMAKE_CURRENT_LIST_DIR}"
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)


#-----------------------------------------------------------------------
# CTest test targets

openassetio_add_test_target(openassetio.internal.pytest.module)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.pytest.module
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.pytest.module)
