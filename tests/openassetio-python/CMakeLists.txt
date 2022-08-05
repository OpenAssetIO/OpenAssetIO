#-----------------------------------------------------------------------
# Python test module target for creating test-only bindings.

add_library(openassetio-python-test MODULE)
set_default_target_properties(openassetio-python-test)

set(install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-test
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${install_subdir}
)

# Set Python extension module name, and remove any ("lib") prefix.
set_target_properties(openassetio-python-test
    PROPERTIES
    OUTPUT_NAME _openassetio_test
    PREFIX ""
    # Python modules on macOS must be .so rather than .dylib. But that
    # means clang will complain:
    #   invalid argument '-compatibility_version 1.0.0' only allowed
    #   with '-dynamiclib'
    # Similarly for '-current_version'.So unset the version flags. See
    # also https://cmake.org/cmake/help/latest/prop_tgt/VERSION.html#mach-o-versions)
    SOVERSION ""
    VERSION "")

if (WIN32)
    set_target_properties(openassetio-python-test PROPERTIES SUFFIX ".pyd")
    install(FILES $<TARGET_PDB_FILE:openassetio-python-test>
        CONFIGURATIONS "Debug" "RelWithDebInfo"
        DESTINATION ${install_subdir})
endif ()

#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-python-test
    PRIVATE
    _openassetio_test.cpp
    PyRetainingSharedPtrTest.cpp
    hostApiTest.cpp
)

# Give access to private headers.
target_include_directories(openassetio-python-test
    PRIVATE ${PROJECT_SOURCE_DIR}/src/openassetio-python/module)

target_link_libraries(openassetio-python-test
    PRIVATE
    # Core C++ library.
    openassetio-core
    # Python C++ bridge library.
    openassetio-python-bridge
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras)

add_dependencies(openassetio-python-test openassetio-python-module)

#-----------------------------------------------------------------------
# Override build tree to look like install tree.

set_target_properties(openassetio-python-test
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir}
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir})


#-----------------------------------------------------------------------
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
# Create test targets

if (Python_Interpreter_FOUND)
    # Directory to find/download dependencies. We try to cache downloads
    # so that people can work offline.
    set(python_deps_dir "${CMAKE_BINARY_DIR}/dependencies/python")

    # Get path to Python executable in the created venv, and a way to activate
    # the venv itself.
    if (WIN32)
        set(venv_activate "${CMAKE_INSTALL_PREFIX}/Scripts/activate.bat")
        set(venv_python_exe "${CMAKE_INSTALL_PREFIX}/Scripts/python.exe")
    else ()
        set(venv_activate . "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/activate")
        set(venv_python_exe "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/python")
    endif ()

    # Download test-specific dependencies so we don't always need an
    # online connection for running ctest
    add_custom_target(
        openassetio-python-test-download-test-deps
        COMMAND ${CMAKE_COMMAND} -E echo -- Downloading Python test libraries
        COMMAND
        ${Python_EXECUTABLE} -m pip download
        --retries 0 --timeout ${OPENASSETIO_PYTHON_PIP_TIMEOUT}
        --find-links ${python_deps_dir}
        --destination-directory ${python_deps_dir}
        --requirement "${PROJECT_SOURCE_DIR}/tests/python/requirements.txt"
        --requirement "${PROJECT_SOURCE_DIR}/resources/codegen/tests/requirements.txt"
    )

    # Install test-specific dependencies (e.g. pytest).
    add_custom_target(
        openassetio-python-test-install-test-deps
        COMMAND cmake -E echo -- Installing Python test dependencies
        COMMAND
        ${venv_python_exe} -m pip install
        --no-index --find-links ${python_deps_dir}
        --requirement "${PROJECT_SOURCE_DIR}/tests/python/requirements.txt"
        --requirement "${PROJECT_SOURCE_DIR}/resources/codegen/tests/requirements.txt"
    )
    add_dependencies(openassetio-python-test-install-test-deps
        # Ensure venv pip is available and up-to-date.
        openassetio-python-venv
        # Ensure dependencies have been downloaded
        openassetio-python-test-download-test-deps)

    # Add ASan-specific environment variables to prepend to the `pytest`
    # invocation.
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

    # Target to run pytest in the install directory, ensuring the lib has
    # been built and installed first. Add `-s` to ensure no output is
    # captured, which is needed to show sanitizer errors (and is useful
    # for debugging regardless).
    add_custom_target(
        openassetio-python-test-pytest
        COMMAND cmake -E echo -- Running pytest
        COMMAND ${venv_activate} && ${pytest_env} ${venv_python_exe} -m pytest -v --capture=tee-sys
        tests/python
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
        USES_TERMINAL
    )
    add_dependencies(openassetio-python-test-pytest
        openassetio-python-test-install-test-deps openassetio-python-py-install)

    # Target to run tests on examples included in the resources
    # directory.
    add_custom_target(
        openassetio-resources-examples-test-pytest
        COMMAND cmake -E echo -- Running pytest
        COMMAND ${venv_activate} && ${pytest_env} ${venv_python_exe} -m pytest -v --capture=tee-sys
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/resources/examples"
        USES_TERMINAL
    )
    add_dependencies(openassetio-resources-examples-test-pytest
        openassetio-python-test-install-test-deps openassetio-python-py-install)

    # Target to run tests on the openassetio-codegen tool included in
    # the resources directory.
    add_custom_target(
        openassetio-resources-codegen-test-pytest
        COMMAND cmake -E echo -- Running pytest
        COMMAND ${venv_activate} && ${pytest_env} ${venv_python_exe} -m pytest -v --capture=tee-sys
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/resources/codegen"
        USES_TERMINAL
    )
    add_dependencies(openassetio-resources-codegen-test-pytest
        openassetio-python-test-install-test-deps openassetio-python-py-install
        openassetio-resources-codegen-install)

    # Add CTest targets.

    add_test(
        NAME openassetio-python
        COMMAND
        ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target openassetio-python-test-pytest
    )

    add_test(
        NAME openassetio-resources-examples
        COMMAND
        ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target
        openassetio-resources-examples-test-pytest
    )

    add_test(
        NAME openassetio-resources-codegen
        COMMAND
        ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target
        openassetio-resources-codegen-test-pytest
    )
endif ()
