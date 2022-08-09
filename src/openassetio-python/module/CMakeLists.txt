#-----------------------------------------------------------------------
# Python module target

add_library(openassetio-python-module MODULE)
set_default_target_properties(openassetio-python-module)

set(install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-module
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${install_subdir}
)

# Set Python extension module name, and remove any ("lib") prefix.
set_target_properties(openassetio-python-module
    PROPERTIES
    OUTPUT_NAME _openassetio
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
    set_target_properties(openassetio-python-module PROPERTIES SUFFIX ".pyd")
    install(FILES $<TARGET_PDB_FILE:openassetio-python-module>
        CONFIGURATIONS "Debug" "RelWithDebInfo"
        DESTINATION ${install_subdir})
endif ()

#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-python-module
    PRIVATE
    _openassetio.cpp
    ContextBinding.cpp
    EntityReferenceBinding.cpp
    TraitsDataBinding.cpp
    hostApi/ManagerBinding.cpp
    hostApi/HostInterfaceBinding.cpp
    hostApi/ManagerFactoryBinding.cpp
    hostApi/ManagerImplementationFactoryInterfaceBinding.cpp
    log/ConsoleLoggerBinding.cpp
    log/LoggerInterfaceBinding.cpp
    log/SeverityFilterBinding.cpp
    managerApi/HostBinding.cpp
    managerApi/HostSessionBinding.cpp
    managerApi/ManagerInterfaceBinding.cpp
    managerApi/ManagerStateBaseBinding.cpp
)

target_link_libraries(openassetio-python-module
    PRIVATE
    # Core C++ library.
    openassetio-core
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras)

target_include_directories(openassetio-python-module
    PRIVATE
    # Common helpers only available at build time.
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../private/include>")

#-----------------------------------------------------------------------
# Override build tree to look like install tree.

set_target_properties(openassetio-python-module
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

    set_target_properties(openassetio-python-module PROPERTIES INSTALL_RPATH "${rpath}")
endif ()


#-----------------------------------------------------------------------
# Create deployment targets

if (Python_Interpreter_FOUND)
    # Get path to Python executable in the created venv.
    if (WIN32)
        set(venv_python_exe "${CMAKE_INSTALL_PREFIX}/Scripts/python.exe")
    else ()
        set(venv_python_exe "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/python")
    endif ()

    # Download core setuptools dependencies so we don't always need an
    # online connection to local install OpenAssetIO. Need to cache the
    # build tools explicitly due to build isolation, see:
    # https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-process
    # This also includes runtime dependencies of packages in the
    # resources directory, whose install will otherwise fail due to
    # --no-index.
    set(python_deps_dir "${CMAKE_BINARY_DIR}/dependencies/python")
    add_custom_target(
        openassetio-python-download-deps
        COMMAND ${CMAKE_COMMAND} -E echo -- Downloading core Python libraries
        COMMAND
        ${Python_EXECUTABLE} -m pip download
        --retries 0 --timeout ${OPENASSETIO_PYTHON_PIP_TIMEOUT} --find-links ${python_deps_dir}
        --destination-directory ${python_deps_dir}
        wheel==0.37.1 setuptools==49.0
        --requirement "${PROJECT_SOURCE_DIR}/resources/codegen/requirements.txt"
    )
    # Create a Python environment in the install directory. If the venv
    # already exists then this is a no-op.
    add_custom_target(
        openassetio-python-venv
        COMMAND ${CMAKE_COMMAND} -E echo -- Creating Python environment in ${CMAKE_INSTALL_PREFIX}
        COMMAND ${Python_EXECUTABLE} -m venv ${CMAKE_INSTALL_PREFIX}
        # Install `wheel` so that setuptools can build OpenAssetIO.
        COMMAND
        ${venv_python_exe} -m pip install --no-index --find-links ${python_deps_dir}
        wheel setuptools
    )
    add_dependencies(openassetio-python-venv
        # Ensure dependencies have been downloaded for constructing the
        # venv.
        openassetio-python-download-deps)

    # Install OpenAssetIO into the venv.
    add_custom_target(
        openassetio-python-py-install
        COMMAND ${CMAKE_COMMAND} -E echo -- Installing OpenAssetIO
        COMMAND
        ${venv_python_exe} -m pip install
        # For speed, build from the venv rather than copying the whole
        # project to a temporary environment. Note that this is a pip
        # feature, setuptools also has its own build cache (see
        # setup.cfg). This flag roughly halves test runtime.
        --no-build-isolation
        --no-index --find-links ${python_deps_dir}
        ${PROJECT_SOURCE_DIR}
    )
    add_dependencies(openassetio-python-py-install
        # Ensure C++ component has been installed.
        openassetio-install
        # Ensure venv is available.
        openassetio-python-venv)

    # Install OpenAssetIO Code Generator into the venv.
    add_custom_target(
        openassetio-resources-codegen-install
        COMMAND ${CMAKE_COMMAND} -E echo -- Installing OpenAssetIO Code Generator
        COMMAND
        ${venv_python_exe} -m pip install
        # For speed, build from the venv rather than copying the whole
        # project to a temporary environment. Note that this is a pip
        # feature, setuptools also has its own build cache (see
        # setup.cfg). This flag roughly halves test runtime.
        --no-build-isolation
        --no-index --find-links ${python_deps_dir}
        ${PROJECT_SOURCE_DIR}/resources/codegen
    )
    add_dependencies(openassetio-resources-codegen-install
        # Ensure venv is available.
        openassetio-python-venv)
endif ()
