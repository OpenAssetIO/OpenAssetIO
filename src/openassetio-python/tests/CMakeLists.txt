# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# Python/C++ bridge tests

add_subdirectory(bridge)


#-----------------------------------------------------------------------
# Python test module target for creating test-only bindings.

add_subdirectory(internal/resources/_openassetio_test)


#-----------------------------------------------------------------------
# Core Python pytest targets.

# Install test-specific dependencies (e.g. pytest).
openassetio_add_python_environment_dependency(
    openassetio.internal.python-pytest.install-deps
    "${PROJECT_SOURCE_DIR}/src/openassetio-python/tests/requirements.txt"
)

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.python-pytest.package
    "Running pytest for core Python"
    src/openassetio-python/tests/package
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.python-pytest.internal
    "Running pytest for Python binding helpers"
    src/openassetio-python/tests/internal
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)

#-----------------------------------------------------------------------
# CTest test targets

# Core Python component tests.
openassetio_add_test_target(openassetio.internal.python-pytest.package)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-pytest.package
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.python-pytest.package)

# Python bindings helpers tests.
openassetio_add_test_target(openassetio.internal.python-pytest.internal)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-pytest.internal
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.python-pytest.internal)
