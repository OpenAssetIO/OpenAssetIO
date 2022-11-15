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
# Gather ASan-specific environment variables to prepend to the `pytest`
# invocations.

if (OPENASSETIO_ENABLE_SANITIZER_ADDRESS AND IS_GCC_OR_CLANG)
    # ASan will error out if libasan is not the first library to be
    # linked (so it can override `malloc`). Since our executable
    # (`python` in this case) doesn't link libasan we must add it to
    # `LD_PRELOAD`. But first we have to find libasan on the system:
    execute_process(
        # TODO(DF): This is probably wrong for OSX (clang).
        COMMAND ${CMAKE_CXX_COMPILER} -print-file-name=libasan.so
        OUTPUT_VARIABLE asan_path
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    # ASan can hang on exceptions when `dlopen`ed libraries are
    # involved (i.e. Python extension modules)
    # See: https://bugs.llvm.org/show_bug.cgi?id=39641
    # or: https://github.com/llvm/llvm-project/issues/38989
    # and: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=91325#c5
    # The latter link indicates this bug is fixed in GCC 10.1, but
    # we're stuck with 9.3 (CY21/22) for now.
    # To work around this we must LD_PRELOAD our core lib.
    set(openassetio_path
        ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}/$<TARGET_FILE_NAME:openassetio-core>)
    # In addition to `LD_PRELOAD`ing we must override Python's
    # memory allocator to use the C (or rather, ASan's) `malloc`
    # rather than the optimized `pymalloc`, so that ASan can
    # properly count memory (de)allocations.
    set(pytest_env PYTHONMALLOC=malloc LD_PRELOAD=${asan_path}:${openassetio_path})
endif ()


#-----------------------------------------------------------------------
# Core Python pytest targets.

# Add target that runs pytest.
#
# Add `--capture=tee-sys` to ensure output shows sanitizer errors (and
# is useful for debugging regardless).
function(openassetio_add_pytest_target
         target_name description target_directory working_directory)

    # Account for windows not being able to set variables inline
    if (WIN32)
        list(JOIN ARGN $<SEMICOLON> pythonpath)
        set(combined_pytest_env set PYTHONPATH=${pythonpath} ${pytest_env})
    else()
        list(JOIN ARGN ":" pythonpath)
        set(combined_pytest_env export PYTHONPATH=${pythonpath} ${pytest_env})
    endif()

    add_custom_target(
        ${target_name}
        COMMAND cmake -E echo -- ${description}
        COMMAND ${combined_pytest_env} &&
        ${OPENASSETIO_PYTHON_EXE} -m pytest -v --capture=tee-sys
        ${target_directory}
        WORKING_DIRECTORY "${working_directory}"
        USES_TERMINAL
    )
endfunction()

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
# CTest setup fixtures

# Optional fixture dependency to create a Python environment in the
# install tree.
set(_venv_if_enabled )
if (OPENASSETIO_ENABLE_PYTHON_TEST_VENV)
    # Fixture: create Python environment.
    openassetio_add_test_fixture_target(openassetio-python-venv)
    set(_venv_if_enabled openassetio-python-venv)
endif ()


#-----------------------------------------------------------------------
# CTest test targets

# Core Python component tests.
openassetio_add_test_target(openassetio.internal.python-pytest)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-pytest
    openassetio.internal.install
    ${_venv_if_enabled}
)

# Examples tests.
openassetio_add_test_target(openassetio.internal.resources-examples-pytest)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.resources-examples-pytest
    openassetio.internal.install
    ${_venv_if_enabled}
)
