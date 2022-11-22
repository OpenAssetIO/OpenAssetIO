#-----------------------------------------------------------------------
# Python test module target for creating test-only bindings.

pybind11_add_module(openassetio-python-test MODULE)
# Set target file name to `_openassetio_test`
openassetio_set_default_target_properties(openassetio-python-test)
set_target_properties(
    openassetio-python-test PROPERTIES
    OUTPUT_NAME _openassetio_test
    SOVERSION ""
    VERSION ""
)

set(install_subdir "${OPENASSETIO_PYTHON_SITEDIR}/openassetio")

# Add to the set of installable targets.
install(
    TARGETS openassetio-python-test
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${install_subdir}
)

if (WIN32)
    install(
        FILES $<TARGET_PDB_FILE:openassetio-python-test>
        TYPE BIN
        CONFIGURATIONS "Debug" "RelWithDebInfo"
    )
endif ()

target_sources(
    openassetio-python-test
    PRIVATE
    _openassetio_test.cpp
    PyRetainingSharedPtrTest.cpp
)

# Give access to private headers.
target_include_directories(openassetio-python-test
    PRIVATE ${PROJECT_SOURCE_DIR}/src/openassetio-python/module/src)

target_link_libraries(openassetio-python-test
    PRIVATE
    # Core C++ library.
    openassetio-core
    # Python C++ bridge library.
    openassetio-python-bridge
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras)

add_dependencies(openassetio-python-test openassetio-python-module)

# Override build tree to look like install tree.
set_target_properties(openassetio-python-test
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir}
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${install_subdir})

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
