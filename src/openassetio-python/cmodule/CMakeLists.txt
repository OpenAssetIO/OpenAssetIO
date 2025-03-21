#-----------------------------------------------------------------------
# Python module target

# Use pybind11's utility to ensure proper SOABI, file extension, etc is
# used. The rules can be quite tricky, e.g. Windows SOABI suffix is
# quite different for Debug vs. Release builds.
pybind11_add_module(openassetio-python-module MODULE)
openassetio_set_default_target_properties(openassetio-python-module)
set_target_properties(
    openassetio-python-module
    PROPERTIES
    # Set target file name to `_openassetio`
    OUTPUT_NAME _openassetio
    # Python modules on macOS must be .so rather than .dylib. But that
    # means clang will complain:
    #   invalid argument '-compatibility_version 1.0.0' only allowed
    #   with '-dynamiclib'
    # Similarly for '-current_version'.So unset the version flags. See
    # also https://cmake.org/cmake/help/latest/prop_tgt/VERSION.html#mach-o-versions)
    SOVERSION ""
    VERSION ""
)

add_library(${PROJECT_NAME}::openassetio-python-module ALIAS openassetio-python-module)

set(_install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-module
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${_install_subdir}
    COMPONENT openassetio-python-distribution
)
if (BUILD_SHARED_LIBS)
    # For a shared library build, we must ensure C++ library
    # dependencies are installed when the Python extension module
    # component is installed. The openassetio-python-distribution
    # component is targeted for install when building Python wheels -
    # see setup.py.
    install(
        TARGETS openassetio-core openassetio-python-bridge openassetio-ui
        COMPONENT openassetio-python-distribution
    )
endif ()


#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-python-module
    PRIVATE
    src/_openassetio.cpp
    src/accessBinding.cpp
    src/constantsBinding.cpp
    src/ContextBinding.cpp
    src/EntityReferenceBinding.cpp
    src/versionBinding.cpp
    src/errors/exceptionsAsserts.cpp
    src/errors/exceptionsBinding.cpp
    src/errors/BatchElementErrorBinding.cpp
    src/hostApi/EntityReferencePagerBinding.cpp
    src/hostApi/ManagerBinding.cpp
    src/hostApi/HostInterfaceBinding.cpp
    src/hostApi/ManagerFactoryBinding.cpp
    src/hostApi/ManagerImplementationFactoryInterfaceBinding.cpp
    src/log/ConsoleLoggerBinding.cpp
    src/log/LoggerInterfaceBinding.cpp
    src/log/SeverityFilterBinding.cpp
    src/managerApi/HostBinding.cpp
    src/managerApi/HostSessionBinding.cpp
    src/managerApi/EntityReferencePagerInterfaceBinding.cpp
    src/managerApi/ManagerInterfaceBinding.cpp
    src/managerApi/ManagerStateBaseBinding.cpp
    src/pluginSystem/CppPluginSystemBinding.cpp
    src/pluginSystem/CppPluginSystemPluginBinding.cpp
    src/pluginSystem/CppPluginSystemManagerImplementationFactoryBinding.cpp
    src/pluginSystem/HybridPluginSystemManagerImplementationFactoryBinding.cpp
    src/trait/TraitsDataBinding.cpp
    src/utilsBinding.cpp
    src/ui/hostApi/UIDelegateImplementationFactoryInterfaceBinding.cpp
    src/ui/hostApi/UIDelegateFactoryBinding.cpp
    src/ui/hostApi/UIDelegateBinding.cpp
    src/ui/managerApi/UIDelegateInterfaceBinding.cpp
    src/ui/pluginSystem/CppPluginSystemUIDelegateImplementationFactoryBinding.cpp
    src/ui/pluginSystem/HybridPluginSystemUIDelegateImplementationFactoryBinding.cpp
)

target_link_libraries(openassetio-python-module
    PRIVATE
    # Core C++ library.
    openassetio-core
    # UI delegation library.
    openassetio-ui
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras
    $<BUILD_INTERFACE:fmt::fmt-header-only>
)

target_include_directories(openassetio-python-module
    PRIVATE
    # Common helpers only available at build time.
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../private/include>")

#-----------------------------------------------------------------------
# Override build tree to look like install tree.

set_target_properties(openassetio-python-module
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${_install_subdir}
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${_install_subdir})


#-----------------------------------------------------------------------
# Override RPATH in (usual) case that Python .so and core .so live in
# different locations.

if (UNIX)
    # Calculate relative path from site-packages to lib directory.
    file(RELATIVE_PATH
        install_dir_rel_to_lib
        "${CMAKE_INSTALL_PREFIX}/${_install_subdir}"
        "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")

    if (APPLE)
        set(_rpath "@loader_path/${install_dir_rel_to_lib}")
    else ()
        set(_rpath "$ORIGIN/${install_dir_rel_to_lib}")
    endif ()

    set_target_properties(openassetio-python-module PROPERTIES INSTALL_RPATH "${_rpath}")
endif ()


#-----------------------------------------------------------------------
# Link in the test-specific bindings, if testing is enabled.
#
# In order to have representative tests of Python extension module
# internals we, unfortunately, need to bundle test functionality within
# the _openassetio module itself.

if (OPENASSETIO_ENABLE_TESTS)
    target_compile_definitions(openassetio-python-module PRIVATE OPENASSETIO_ENABLE_TESTS)
    target_link_libraries(openassetio-python-module PRIVATE openassetio-python-module-test)
endif ()


#-----------------------------------------------------------------------
# Generate .pyi stubs
#
# pybind11-stubgen will create openassetio/_openassetio subdirectories
# in the build output directory. We use this knowledge to assemble a
# Python pseudo-package in the build output directory, such that stubgen
# can import the module to do its thing then dump its output alongside.

if (OPENASSETIO_ENABLE_PYTHON_STUBGEN)
    # Check pybind11-stubgen is available.
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m pybind11_stubgen --help
        OUTPUT_VARIABLE _pybind11_stubgen_output
        ERROR_VARIABLE _pybind11_stubgen_output
        RESULT_VARIABLE _pybind11_stubgen_exit_code
    )

    # Fatal error if pybind11-stubgen isn't available.
    if (NOT _pybind11_stubgen_exit_code EQUAL "0")
        message(
            FATAL_ERROR
            "OPENASSETIO_ENABLE_PYTHON_STUBGEN=${OPENASSETIO_ENABLE_PYTHON_STUBGEN} but"
            " pybind11-stubgen not found: status=${_pybind11_stubgen_exit_code}:"
            " ${_pybind11_stubgen_output}"
        )
    endif ()

    # Create temporary pseudo-package directory.
    add_custom_command(
        TARGET openassetio-python-module POST_BUILD
        COMMAND
        "${CMAKE_COMMAND}" -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/openassetio"
    )

    if (WIN32)
        # On Windows, copy dll dependencies into the pseudo-package
        # directory, so that stubgen can import _openassetio.
        # Note that this must be done _after_ the build, otherwise
        # Windows (Visual Studio CMake generator) complains that the
        # build directory already exists.
        # Also note OPENASSETIO_DLL_PATH does not work here, since that
        # requires the top-level `openassetio.__init__.py` to be
        # importable, but it lives in a different directory (at build
        # time).
        add_custom_command(
            TARGET openassetio-python-module POST_BUILD
            COMMAND
            "${CMAKE_COMMAND}" -E copy_if_different
            "$<TARGET_FILE:openassetio-core>"
            "${CMAKE_CURRENT_BINARY_DIR}/openassetio/"
            COMMAND
            "${CMAKE_COMMAND}" -E copy_if_different
            "$<TARGET_FILE:openassetio-ui>"
            "${CMAKE_CURRENT_BINARY_DIR}/openassetio/"
        )
    endif ()

    # Execute commands to generate .pyi stubs.
    add_custom_command(
        TARGET openassetio-python-module POST_BUILD
        COMMAND
        "${CMAKE_COMMAND}" -E echo "Generating .pyi stubs with pybind11-stubgen..."
        # Copy the Python extension module under the pseudo-package
        # directory.
        COMMAND
        "${CMAKE_COMMAND}" -E copy_if_different
        "$<TARGET_FILE:openassetio-python-module>"
        "${CMAKE_CURRENT_BINARY_DIR}/openassetio/"
        # Ensure we have a py.typed file at the root of our package, to
        # signal to IDEs that stubs exist.
        COMMAND
        "${CMAKE_COMMAND}" -E touch "${CMAKE_CURRENT_BINARY_DIR}/openassetio/py.typed"
        # Execute pybind11-stubgen, modifying PYTHONPATH so it can
        # locate the openassetio._openassetio module.
        COMMAND
        "${CMAKE_COMMAND}" -E env
        --modify "PYTHONPATH=path_list_prepend:${CMAKE_CURRENT_BINARY_DIR}"
        --
        "${Python_EXECUTABLE}" -m pybind11_stubgen
        # Fail the build and abort if any errors generating stubs.
        --exit-code
        # For whatever reason, stubgen fails to resolve PathType.
        --enum-class-locations PathType:openassetio._openassetio.utils
        -o "${CMAKE_CURRENT_BINARY_DIR}" openassetio._openassetio
        VERBATIM
    )

    # Add stub files to the Python extension module installation
    # component, so that
    # `cmake --install --component openassetio-python-distribution` will
    # include the stubs.
    install(
        # pybind11-stubgen generates stubs for openassetio._openassetio
        # under an `openassetio/_openassetio` directory structure.
        DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/openassetio/_openassetio"
        DESTINATION "${_install_subdir}"
        COMPONENT openassetio-python-distribution
    )
    install(
        FILES "${CMAKE_CURRENT_BINARY_DIR}/openassetio/py.typed"
        DESTINATION "${_install_subdir}"
        COMPONENT openassetio-python-distribution
    )
endif ()
