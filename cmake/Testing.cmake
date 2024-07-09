# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2024 The Foundry Visionmongers Ltd

# Don't re-process this module if it's already included by a project.
include_guard(GLOBAL)
if (NOT ${CMAKE_CURRENT_SOURCE_DIR} STREQUAL ${PROJECT_SOURCE_DIR})
    # Ensure this module is `include`d from the top-level CMakeLists.txt
    # (first), since we rely on this file only being included once (to
    # prevent multiple definitions, e.g. openassetio-python-venv) and
    # need all variables (e.g. find_package targets) to be made
    # available project-wide.
    message(FATAL_ERROR "Testing.cmake must be included in the top-level CMakeLists.txt")
endif ()


#-----------------------------------------------------------------------
# Unit test libraries.

find_package(Catch2 2 REQUIRED)
find_package(trompeloeil 42 REQUIRED)


#-----------------------------------------------------------------------
# Test definition helpers.

# Add a CTest fixture target that runs a CMake build target.
#
# Reuses the target name for both the test name and fixture name.
function(openassetio_add_test_fixture_target target_name)
    openassetio_add_generic_test_target(${target_name})
    set_tests_properties(${target_name} PROPERTIES FIXTURES_SETUP ${target_name})
endfunction()

# Add one or more fixture dependencies to a test.
#
# Multiple space-separated fixtures can be specified. Fixtures will be
# appended to the existing list of fixtures for the test.
function(openassetio_add_test_fixture_dependencies test_name)
    get_test_property(${test_name} FIXTURES_REQUIRED fixtures)
    list(APPEND fixtures ${ARGN})
    set_tests_properties(${test_name} PROPERTIES FIXTURES_REQUIRED "${fixtures}")
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
        COMMAND ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target ${target_name} --parallel
        --config $<CONFIG>
    )
endfunction()

#-----------------------------------------------------------------------
# ABI checker tests.

if (OPENASSETIO_ENABLE_TEST_ABI)
    find_program(OPENASSETIO_ABIDIFF_EXE NAMES abidiff REQUIRED)

    # Create a test to check the ABI compatibility of a target.
    #
    # Uses libabigail's `abidiff` tool, and assumes .xml snapshots with
    # the same name as the library, under `resources/abi` in the
    # project root.
    #
    # Uses the build artifact location for convenience (i.e. handy
    # generator expressions to get the path), rather than the install
    # artifacts, but they are equivalent for `abidiff` purposes.
    function(openassetio_add_abi_test_target target_name)
        add_custom_target(
            openassetio.test.abi.${target_name}
            # Empty echos to print newlines.
            COMMAND ${CMAKE_COMMAND} -E echo
            COMMAND ${CMAKE_COMMAND} -E echo
            "===== Checking ABI of $<TARGET_FILE_NAME:${target_name}> ====="
            COMMAND ${CMAKE_COMMAND} -E echo
            COMMAND ${OPENASSETIO_ABIDIFF_EXE}
            # Ensure we have a Debug build to extract symbol info from.
            --fail-no-debug-info
            # Reduce output to just salient info. I.e. skip the  "impact
            # analysis" tree showing an example function that is
            # affected by the change.
            --leaf-changes-only
            # TODO(DF): Bug in libabigail 2.4 `default.abignore` default
            # suppression file causes false negatives. Any ABI break
            # involving a function with `std::` in the demangled name is
            # suppressed - this includes template specialisations, e.g.
            # `castToPyObject<std::shared_ptr<...`.
            --no-default-suppression
            ${PROJECT_SOURCE_DIR}/resources/abi/$<TARGET_FILE_NAME:${target_name}>.xml
            $<TARGET_FILE:${target_name}>
        )
        openassetio_add_test_target(openassetio.test.abi.${target_name})
        openassetio_add_test_fixture_dependencies(
            openassetio.test.abi.${target_name}
            openassetio.internal.install
        )
    endfunction()
endif ()

#-----------------------------------------------------------------------
# Fixture to ensure install tree has been generated
#
# For better dogfooding we run all our tests in the install tree, so
# this fixture should be a dependency of all tests.
openassetio_add_test_fixture_target(openassetio.internal.install)


#-----------------------------------------------------------------------
# Variables for use in tests.

# Subdirectory under INSTALL_PREFIX where C++ test plugins will be
# installed
set(OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR ${CMAKE_INSTALL_LIBDIR}/${PROJECT_NAME}/plugins)


#-----------------------------------------------------------------------
# Python-specific helpers

if (OPENASSETIO_ENABLE_PYTHON)

    #-------------------------------------------------------------------
    # Optional Python virtualenv to run tests in.

    if (OPENASSETIO_ENABLE_PYTHON_TEST_VENV)
        openassetio_add_test_fixture_target(openassetio-python-venv)
    endif ()

    # Add test virtualenv as a fixture dependency of a given test
    # target.
    #
    # This is a no-op if OPENASSETIO_ENABLE_PYTHON_TEST_VENV is false.
    function(openassetio_add_test_venv_fixture_dependency target_name)
        if (OPENASSETIO_ENABLE_PYTHON_TEST_VENV)
            openassetio_add_test_fixture_dependencies(${target_name} openassetio-python-venv)
        endif ()
    endfunction()

    #-------------------------------------------------------------------
    # Common environment variables for pytest tests.

    set(
        _pytest_env
        OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR=${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}
        OPENASSETIO_TEST_ENABLE_PYTHON_STUBGEN=$<BOOL:${OPENASSETIO_ENABLE_PYTHON_STUBGEN}>
    )

    #-------------------------------------------------------------------
    # Gather ASan-specific environment variables to prepend to the
    # `pytest` invocations.

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
        set(_openassetio_path
            ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}/$<TARGET_FILE_NAME:openassetio-core>)
        # In addition to `LD_PRELOAD`ing we must override Python's
        # memory allocator to use the C (or rather, ASan's) `malloc`
        # rather than the optimized `pymalloc`, so that ASan can
        # properly count memory (de)allocations.
        set(_pytest_env
            PYTHONMALLOC=malloc LD_PRELOAD=${asan_path}:${_openassetio_path} ${_pytest_env})
    endif ()


    #-------------------------------------------------------------------
    # Add target that runs pytest.
    #
    # Add `--capture=tee-sys` to ensure output shows sanitizer errors
    # (and is useful for debugging regardless).
    function(openassetio_add_pytest_target
        target_name description target_directory working_directory)
        if (WIN32)
            list(JOIN ARGN $<SEMICOLON> pythonpath)
        else ()
            list(JOIN ARGN ":" pythonpath)
        endif ()
        set(pytest_env PYTHONPATH=${pythonpath} ${_pytest_env})

        add_custom_target(
            ${target_name}
            COMMAND ${CMAKE_COMMAND} -E echo -- ${description}
            COMMAND ${CMAKE_COMMAND} -E env ${pytest_env}
            ${OPENASSETIO_PYTHON_EXE} -m pytest -v --capture=tee-sys
            ${target_directory}
            WORKING_DIRECTORY "${working_directory}"
            USES_TERMINAL
        )
    endfunction()
endif ()
