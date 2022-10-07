find_package(Catch2 2 REQUIRED)
find_package(trompeloeil 42 REQUIRED)

# Add a CTest fixture target that runs a CMake build target.
#
# Reuses the target name for both the test name and fixture name.
function(openassetio_add_test_fixture_target target_name)
    openassetio_add_generic_test_target(${target_name})
    set_tests_properties(${target_name} PROPERTIES FIXTURES_SETUP ${target_name})
endfunction()

# Add one or more fixture dependencies to a test.
#
# Since FIXTURES_REQUIRED expects a list, this little function acts as
# a convenience to transform whitespace-separated arguments to a CMake
# list (semicolon-separated).
function(openassetio_add_test_fixture_dependencies test_name)
    set_tests_properties(${test_name} PROPERTIES FIXTURES_REQUIRED "${ARGN}")
endfunction()

# Create a CTest test target from a CMake build target.
#
# Reuses the target name for the test name.
#
# Adds the "Test" label to allow filtering. I.e. unit tests have the
# "Test" label, whereas fixture tests do not. This then allows devs to
# skip unnecessary fixtures, e.g.
#   ctest -FA 'openassetio-python-venv' -L Test
# will skip creating the Python environment and downloading and
# installing dependencies.
function(openassetio_add_test_target target_name)
    openassetio_add_generic_test_target(${target_name})
    set_tests_properties(${target_name} PROPERTIES LABELS Test)
endfunction()

# Create a generic CTest test target from a CMake build target.
#
# Reuses the target name for the test name.
function(openassetio_add_generic_test_target target_name)
    add_test(
        NAME ${target_name}
        COMMAND ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target ${target_name}
    )
endfunction()


# Add fixture test to be used as a dependency of other tests.
openassetio_add_test_fixture_target(openassetio.internal.install)

# Core C++ API tests.
add_subdirectory(openassetio-core)

# C API bindings tests.
if (OPENASSETIO_ENABLE_C)
    add_subdirectory(openassetio-core-c)
endif ()

# Python tests.
if (OPENASSETIO_ENABLE_PYTHON)
    add_subdirectory(openassetio-python)
endif ()
