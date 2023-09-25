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
    COMPONENT openassetio-python-module
)


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
    src/TraitsDataBinding.cpp
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
