# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Foundry Visionmongers Ltd

# Detect the best Python interpreter to use for running pytest.
# 1. If OPENASSETIO_PYTHON_EXE is defined, use that. This will be set
#    by the parent OpenAssetIO project.
# 2. Otherwise, use the external environment's python.
if (NOT DEFINED OPENASSETIO_PYTHON_EXE)
    set(OPENASSETIO_PYTHON_EXE python)
endif ()

# Construct list of environment variables to use for tests.

if (DEFINED OPENASSETIO_PYTHON_SITEDIR)
    # E.g. we're running tests via OpenAssetIO parent project, so we
    # know the PYTHONPATH we need to use.
    list(APPEND _envmod --modify "PYTHONPATH=path_list_append:${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}")
endif ()

list(APPEND _envmod
    "OPENASSETIO_PLUGIN_PATH=${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_SIMPLECPPMANAGER_INSTALL_SUBDIR}")

list(APPEND _envmod
    "OPENASSETIO_DEFAULT_CONFIG=${CMAKE_CURRENT_SOURCE_DIR}/resources/openassetio_config.toml")

list(APPEND _envmod "OPENASSETIO_LOGGING_SEVERITY=1")

# Add pytest test
add_test(
    NAME openassetio.example.${PROJECT_NAME}.pytest
    COMMAND
    ${CMAKE_COMMAND} -E env ${_envmod}
    ${OPENASSETIO_PYTHON_EXE} -m pytest -v --capture=tee-sys ${CMAKE_CURRENT_SOURCE_DIR}
)

# Add openassetio.test.manager API compliance suite test.
add_test(
    NAME openassetio.example.${PROJECT_NAME}.apiCompliance
    COMMAND
    ${CMAKE_COMMAND} -E env ${_envmod}
    ${OPENASSETIO_PYTHON_EXE} -m openassetio.test.manager -f ${CMAKE_CURRENT_SOURCE_DIR}/resources/fixtures.py
)

# Check if we're running as part of OpenAssetIO's build. Ideally we'd
# use `if (TEST` here, but that only works in the same or parent
# directories where the `install` fixture was defined, apparently.
if (TARGET openassetio.internal.install)
    # We're running as part of OpenAssetIO's build, so ensure it is
    # built and installed before running the tests.
    set_tests_properties(
        openassetio.example.${PROJECT_NAME}.pytest
        PROPERTIES
        FIXTURES_REQUIRED openassetio.internal.install
        LABELS Test
    )
    set_tests_properties(
        openassetio.example.${PROJECT_NAME}.apiCompliance
        PROPERTIES
        FIXTURES_REQUIRED openassetio.internal.install
        LABELS Test
    )
endif ()
