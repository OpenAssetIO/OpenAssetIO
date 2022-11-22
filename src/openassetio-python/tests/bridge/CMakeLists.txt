# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# C++/Python bridge test target

add_executable(openassetio-python-bridge-test-exe)

set_target_properties(
    openassetio-python-bridge-test-exe
    PROPERTIES
    # Export symbols despite being an executable, so dynamically loaded
    # Python extension modules can access them.
    ENABLE_EXPORTS ON
)
openassetio_set_default_target_properties(openassetio-python-bridge-test-exe)
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
    python/test_hostApi.cpp
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
# Create CTest target

add_custom_target(
    openassetio.internal.python-bridge-test
    COMMAND
    ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/$<TARGET_FILE_NAME:openassetio-python-bridge-test-exe>
)

openassetio_add_test_target(openassetio.internal.python-bridge-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.python-bridge-test
    openassetio.internal.install
)


#-----------------------------------------------------------------------
# Set CTest target's environment variables

# Since we're not a "real" Python distribution, we're missing all the
# required Python libraries. So to work around this, set PYTHONHOME to
# point to the Python distribution that we inherited from.
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import sys; sys.stdout.write(sys.prefix)"
    OUTPUT_VARIABLE Python_PREFIX
)
list(APPEND _envvars "PYTHONHOME=${Python_PREFIX}")
# Add the openassetio package to the Python search path.
list(APPEND _envvars "PYTHONPATH=${CMAKE_INSTALL_PREFIX}/${OPENASSETIO_PYTHON_SITEDIR}")
# Set OpenAssetIO's plugin search path.
list(APPEND _envvars "OPENASSETIO_PLUGIN_PATH=${CMAKE_CURRENT_LIST_DIR}/resources")
# Augment the PATH on Windows to find Python library dlls.
if (WIN32)
    list(APPEND _envvars "PATH=${Python_RUNTIME_LIBRARY_DIRS}")
endif ()

set_tests_properties(
    openassetio.internal.python-bridge-test
    PROPERTIES
    ENVIRONMENT "${_envvars}"
)
