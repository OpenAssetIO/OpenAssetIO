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


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-python PRIVATE _openassetio.cpp)

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
