#-----------------------------------------------------------------------
# Python test module target for creating test-only bindings.

pybind11_add_module(openassetio-python-test MODULE)
# Set target file name to `_openassetio_test`
set_default_target_properties(openassetio-python-test)
set_target_properties(
    openassetio-python-test PROPERTIES
    OUTPUT_NAME _openassetio_test
    SOVERSION ""
    VERSION ""
)

set(install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-test
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${install_subdir}
)

if (WIN32)
    install(
        FILES $<TARGET_PDB_FILE:openassetio-python-test>
        TYPE BIN
        CONFIGURATIONS "Debug" "RelWithDebInfo"
    )
endif ()

target_sources(
    openassetio-python-test
    PRIVATE
    _openassetio_test.cpp
    PyRetainingSharedPtrTest.cpp
    hostApiTest.cpp
)

# Give access to private headers.
target_include_directories(openassetio-python-test
    PRIVATE ${PROJECT_SOURCE_DIR}/src/openassetio-python/module/src)

target_link_libraries(openassetio-python-test
    PRIVATE
    # Core C++ library.
    openassetio-core
    # Python C++ bridge library.
    openassetio-python-bridge
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras)

add_dependencies(openassetio-python-test openassetio-python-module)

# Override build tree to look like install tree.
set_target_properties(openassetio-python-test
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir}
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir})

# Override RPATH in (usual) case that Python .so and core .so live in
# different locations.
if (UNIX)
    # Calculate relative path from site-packages to lib directory.
    file(RELATIVE_PATH
        install_dir_rel_to_lib
        "${CMAKE_INSTALL_PREFIX}/${install_subdir}"
        "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")

    if (APPLE)
        set(rpath "@loader_path/${install_dir_rel_to_lib}")
    else ()
        set(rpath "$ORIGIN/${install_dir_rel_to_lib}")
    endif ()

    set_target_properties(openassetio-python-test PROPERTIES INSTALL_RPATH "${rpath}")
endif ()


#-----------------------------------------------------------------------
# Core Python pytest targets.

# Install test-specific dependencies (e.g. pytest).
openassetio_add_python_environment_dependency(
    openassetio.internal.python-pytest.install-deps
    "${PROJECT_SOURCE_DIR}/tests/python/requirements.txt"
)

# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.python-pytest
    "Running pytest for core Python"
    tests/python
    "${PROJECT_SOURCE_DIR}"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)


#-----------------------------------------------------------------------
# Example managers pytest target.

# Target to run tests on examples included in the resources
# directory.
# Requires:
# - openassetio.internal.install
# - openassetio-python-venv
openassetio_add_pytest_target(
    openassetio.internal.resources-examples-pytest
    "Running pytest for Manager examples"
    .
    "${PROJECT_SOURCE_DIR}/examples/manager"
    "${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}"
)

# NB: examples/host coverage comes through the integration CI
# as they rely on dependent projects.
# TODO(tc) we need an umbrella repo that we can use for local
# TDD test loop dev that covers the full range of integration
# tests.


#-----------------------------------------------------------------------
# CTest test targets

# Core Python component tests.
openassetio_add_test_target(openassetio.internal.python-pytest)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-pytest
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.python-pytest)

# Examples tests.
openassetio_add_test_target(openassetio.internal.resources-examples-pytest)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.resources-examples-pytest
    openassetio.internal.install
)
openassetio_add_test_venv_fixture_dependency(openassetio.internal.resources-examples-pytest)
