# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

if (OPENASSETIO_ENABLE_TESTS)

    #-------------------------------------------------------------------
    # Example managers pytest target.

    # Target to run tests on examples included in the resources
    # directory.
    # Requires:
    # - openassetio.internal.install
    # - openassetio-python-venv
    openassetio_add_pytest_target(
        openassetio.internal.pytest.resources-examples
        "Running pytest for Manager examples"
        .
        # NB: `host` example coverage comes through the integration CI
        # as it relies on dependent projects.
        # TODO(tc) we need an umbrella repo that we can use for local
        # TDD test loop dev that covers the full range of integration
        # tests.
        "${CMAKE_CURRENT_LIST_DIR}/manager"
        "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
    )

    # CTest test wrapping pytest target.
    openassetio_add_test_target(openassetio.internal.pytest.resources-examples)
    openassetio_add_test_fixture_dependencies(
        openassetio.internal.pytest.resources-examples
        openassetio.internal.install
    )
    openassetio_add_test_venv_fixture_dependency(openassetio.internal.pytest.resources-examples)
endif ()
