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
    COMPONENT openassetio-python-module
)

# Set Python extension module name, and remove any ("lib") prefix.
set_target_properties(openassetio-python-module
    PROPERTIES
    # SOABI is good practice, and is required for `--editable` installs.
    OUTPUT_NAME _openassetio.${Python_SOABI}
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
    BatchElementErrorBinding.cpp
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

# Install OpenAssetIO Code Generator dependencies into the venv.
openassetio_add_python_environment_dependency(
    openassetio.internal.resources-codegen.install-deps
    ${PROJECT_SOURCE_DIR}/resources/codegen/requirements.txt
)
