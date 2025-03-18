# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2025 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# C++/Python bridge test target

add_executable(openassetio-python-bridge-test-exe)

openassetio_set_default_target_properties(openassetio-python-bridge-test-exe)
set_target_properties(
    openassetio-python-bridge-test-exe
    PROPERTIES
    # Export symbols despite being an executable, so dynamically loaded
    # Python extension modules can access them.
    ENABLE_EXPORTS ON
)
# For libpython symbols, if linked as a static lib.
openassetio_allow_static_lib_symbol_export(openassetio-python-bridge-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-bridge-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-python-bridge-test-exe
    PRIVATE
    main.cpp
    python/test_converter.cpp
    python/test_hostApi.cpp
    python/ui/test_hostApi.cpp
)

target_link_libraries(
    openassetio-python-bridge-test-exe
    PRIVATE
    # Test framework.
    Catch2::Catch2
    # Mocking framework.
    trompeloeil::trompeloeil
    # Embeddable Python
    pybind11::embed
    # Lib under test.
    openassetio-python-bridge
)
# Test will load the Python extension module at runtime so we shouldn't
# explicitly link to it. So add it as a dependency to ensure it is
# rebuilt along with this one.
add_dependencies(openassetio-python-bridge-test-exe openassetio-python-module)


#-----------------------------------------------------------------------
# Compute environment variables.

# Since we're not a "real" Python distribution, we're missing all the
# required Python libraries. So to work around this, set PYTHONHOME to
# point to the Python distribution that we inherited from.
# base_prefix is used as it always points to the base python install,
# even if a venv is used to define which python to build against.
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import sys; sys.stdout.write(sys.base_prefix)"
    OUTPUT_VARIABLE Python_PREFIX
)
list(APPEND _envvars PYTHONHOME=${Python_PREFIX})
# Add the openassetio package to the Python search path.
list(APPEND _envvars PYTHONPATH=${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR})
# Set OpenAssetIO's plugin search paths.
list(APPEND _envvars OPENASSETIO_PLUGIN_PATH=${CMAKE_CURRENT_LIST_DIR}/resources)
list(APPEND _envvars OPENASSETIO_UI_PLUGIN_PATH=${CMAKE_CURRENT_LIST_DIR}/resources)
# Augment the PATH on Windows to find Python library dll, if it was
# linked as a shared library.
if (WIN32 AND Python_RUNTIME_LIBRARY_DIRS)
    list(APPEND _envvars PATH=${Python_RUNTIME_LIBRARY_DIRS})
endif ()
# Add necessary env vars to make ASan happy.
if (OPENASSETIO_ENABLE_SANITIZER_ADDRESS AND IS_GCC_OR_CLANG)
    # Ensure Python uses ASan's override of `malloc` rather than its own
    # `pymalloc`.
    list(APPEND _envvars PYTHONMALLOC=malloc)
    # Suppress known (third-party) leaks.
    list(APPEND _envvars LSAN_OPTIONS=suppressions=${CMAKE_CURRENT_LIST_DIR}/lsan_suppressions.txt)
endif ()


#-----------------------------------------------------------------------
# Create CTest target for tests that may import _openassetio

add_custom_target(
    openassetio.internal.python-bridge-test
    COMMAND
    # Note: environment variables set in-line here rather than using
    # `set_tests_properties`. If that function is used then the calling
    # environment is affected. In particular, PYTHONHOME can interfere
    # with CMake itself (if installed as a pip package and so
    # /usr/local/cmake is actually a Python console_script).
    ${CMAKE_COMMAND} -E env ${_envvars}
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-python-bridge-test-exe>"
)

openassetio_add_test_target(openassetio.internal.python-bridge-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-bridge-test
    openassetio.internal.install
)

#-----------------------------------------------------------------------
# Create CTest target for tests that intentionally exclude _openassetio
# This came about from wanting to test the error state of functions
# that use the python interpreter, specifically the errors that happen
# when `_openassetio` hadn't been imported into the python environment.
# We can't just rely on ordering for this, as test execution order
# is non-consistent across platforms.
add_custom_target(
    openassetio.internal.python-bridge-no-openassetio-module-test
    COMMAND
    # Note: environment variables set in-line here rather than using
    # `set_tests_properties`. If that function is used then the calling
    # environment is affected. In particular, PYTHONHOME can interfere
    # with CMake itself (if installed as a pip package and so
    # /usr/local/cmake is actually a Python console_script).
    ${CMAKE_COMMAND} -E env ${_envvars}
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-python-bridge-test-exe>" "[no_openassetio_module]"
)

openassetio_add_test_target(openassetio.internal.python-bridge-no-openassetio-module-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-bridge-no-openassetio-module-test
    openassetio.internal.install
)
