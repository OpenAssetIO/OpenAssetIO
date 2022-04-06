#-----------------------------------------------------------------------
# Python module target

add_library(openassetio-python MODULE)
set_default_target_properties(openassetio-python)

set(install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${install_subdir}
)

# Set Python extension module name, and remove any ("lib") prefix.
set_target_properties(openassetio-python
    PROPERTIES
    OUTPUT_NAME _openassetio
    PREFIX "")

if(WIN32)
    set_target_properties(openassetio-python PROPERTIES SUFFIX ".pyd")
    install(FILES $<TARGET_PDB_FILE:openassetio-python>
        CONFIGURATIONS "Debug" "RelWithDebInfo"
        DESTINATION ${install_subdir})
endif()

#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-python
    PRIVATE
    _openassetio.cpp
    managerAPI/ManagerInterfaceBinding.cpp
    specification/SpecificationBinding.cpp
    trait/BlobTraitBinding.cpp
)

# Give access to private headers.
target_include_directories(openassetio-python PRIVATE ../openassetio-core)

target_link_libraries(openassetio-python
    PRIVATE
    # Core C++ library.
    openassetio-core
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras
)

#-----------------------------------------------------------------------
# Override build tree to look like install tree.

set_target_properties(openassetio-python
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
        # TODO(DF): handle RPATH on OSX - e.g. @rpath vs. @loader_path
    else ()
        set(rpath "$ORIGIN/${install_dir_rel_to_lib}")
    endif ()

    set_target_properties(openassetio-python PROPERTIES INSTALL_RPATH "${rpath}")
endif ()

#-----------------------------------------------------------------------
# Create convenience targets for testing

if (OPENASSETIO_ENABLE_TESTS AND Python_Interpreter_FOUND)

    # set up values that differ between Windows and Unixes
    if(WIN32)
      set(venv_python_dir "${CMAKE_INSTALL_PREFIX}/Scripts")
      set(installed_pip "${venv_python_dir}/pip.exe")
    else()
      set(venv_python_dir "${CMAKE_INSTALL_PREFIX}/bin")
      set(installed_pip "${venv_python_dir}/pip")
    endif()

    # Command to create a Python environment in the install directory.
    add_custom_command(
        OUTPUT
        "${installed_pip}"
        COMMAND
        "${Python_EXECUTABLE}" -m venv "${CMAKE_INSTALL_PREFIX}"
        COMMAND
        ${venv_python_dir}/python -m pip install --upgrade pip
    )
    # Target to wrap the venv command so it can be executed in isolation.
    add_custom_target(
        openassetio-python-venv
        DEPENDS "${installed_pip}"
    )

    # One-time step to download test-specific dependencies
    # so we don't always need an online connection for running ctest
    set(deps_dir "${CMAKE_BINARY_DIR}/dependencies")
    set(python_deps_dir "${deps_dir}/python")
    set(test_deps_dir "${python_deps_dir}/tests")
    set(test_deps_downloaded "${deps_dir}/testDepsDwnld.out")
    add_custom_command(
        OUTPUT "${test_deps_downloaded}"
        COMMAND
        "${installed_pip}" "download" "--destination-directory" "${test_deps_dir}"
            "-r" "${PROJECT_SOURCE_DIR}/tests/requirements.txt"
        COMMAND
        cmake -E touch "${test_deps_downloaded}"
        DEPENDS "${installed_pip}" "${PROJECT_SOURCE_DIR}/tests/requirements.txt"
    )

    # One-time step to download project-specific dependencies
    set(project_deps_dir "${python_deps_dir}/project")
    set(project_deps_downloaded "${deps_dir}/projDepsDwnld.out")
    add_custom_command(
        OUTPUT "${project_deps_downloaded}"
        # Need to cache the build tools explicitely due to build isolation, see
        # https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-process
        COMMAND
        "${installed_pip}" wheel --wheel-dir ${project_deps_dir} setuptools wheel
        COMMAND
        cmake -E touch "${project_deps_downloaded}"
        DEPENDS "${installed_pip}"
    )

    # Command to install test-specific dependencies (e.g. pytest).
    add_custom_command(
        OUTPUT
        "${venv_python_dir}/pytest"
        COMMAND
        "${installed_pip}" "install" "--no-index"
            "--find-links" "${test_deps_dir}"
            "-r" "${PROJECT_SOURCE_DIR}/tests/requirements.txt"
        DEPENDS "${test_deps_downloaded}"
    )

    # Target to install the pure Python component of the project.
    add_custom_target(
        openassetio-python-py-install
        COMMAND
        "${installed_pip}" "install" "--no-index"
            "--find-links" "${project_deps_dir}"
            "${PROJECT_SOURCE_DIR}"
        DEPENDS "${project_deps_downloaded}"
    )
    # Ensure pre-requisite C++ component has been installed first.
    add_dependencies(openassetio-python-py-install openassetio-install)

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
        openassetio-python-pytest
        COMMAND ${pytest_env} "${venv_python_dir}/pytest" -s tests resources
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
        DEPENDS "${venv_python_dir}/pytest"
        USES_TERMINAL
    )
    add_dependencies(openassetio-python-pytest openassetio-python-py-install)

    # Add a CTest target.
    add_test(
        NAME openassetio-python
        COMMAND
        ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target openassetio-python-pytest
    )

endif ()
