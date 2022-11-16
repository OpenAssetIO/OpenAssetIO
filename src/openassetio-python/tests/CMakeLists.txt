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
    openassetio.internal.python-pytest
    "Running pytest for core Python"
    src/openassetio-python/tests/package
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)

#-----------------------------------------------------------------------
# CTest test targets

# Core Python component tests.
openassetio_add_test_target(openassetio.internal.python-pytest)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-pytest
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.python-pytest)
