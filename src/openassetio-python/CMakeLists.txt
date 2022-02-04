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

#-----------------------------------------------------------------------
# Create convenience targets for testing

if (OPENASSETIO_ENABLE_TESTS AND Python_Interpreter_FOUND)

    # Command to create a Python environment in the install directory.
    add_custom_command(
        OUTPUT
        "${CMAKE_INSTALL_PREFIX}/bin/pip"
        COMMAND
        "${Python_EXECUTABLE}" -m venv "${CMAKE_INSTALL_PREFIX}"
    )
    # Target to wrap the venv command so it can be executed in isolation.
    add_custom_target(
        openassetio-python-venv
        DEPENDS "${CMAKE_INSTALL_PREFIX}/bin/pip"
    )

    # Command to install test-specific dependencies (e.g. pytest).
    add_custom_command(
        OUTPUT
        "${CMAKE_INSTALL_PREFIX}/bin/pytest"
        COMMAND
        "${CMAKE_INSTALL_PREFIX}/bin/pip" install -r "${PROJECT_SOURCE_DIR}/tests/requirements.txt"
        DEPENDS "${CMAKE_INSTALL_PREFIX}/bin/pip"
    )

    # Target to install the pure Python component of the project.
    add_custom_target(
        openassetio-python-py-install
        COMMAND "${CMAKE_INSTALL_PREFIX}/bin/pip" install "${PROJECT_SOURCE_DIR}"
        DEPENDS "${CMAKE_INSTALL_PREFIX}/bin/pip"
    )
    # Ensure pre-requisite C++ component has been installed first.
    add_dependencies(openassetio-python-py-install openassetio-install)

    # Target to run pytest in the install directory, ensuring the lib has
    # been built and installed first.
    add_custom_target(
        openassetio-python-pytest
        COMMAND "${CMAKE_INSTALL_PREFIX}/bin/pytest"
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/tests"
        DEPENDS "${CMAKE_INSTALL_PREFIX}/bin/pytest"
    )
    add_dependencies(openassetio-python-pytest openassetio-python-py-install)

    # Add a CTest target.
    add_test(
        NAME openassetio-python
        COMMAND
        ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target openassetio-python-pytest
    )
endif ()
