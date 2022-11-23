# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd


#-----------------------------------------------------------------------
# Python core API test target.

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.pytest.package
    "Running pytest for core Python"
    "${CMAKE_CURRENT_LIST_DIR}"
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)


#-----------------------------------------------------------------------
# CTest test targets

openassetio_add_test_target(openassetio.internal.pytest.package)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.pytest.package
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.pytest.package)
