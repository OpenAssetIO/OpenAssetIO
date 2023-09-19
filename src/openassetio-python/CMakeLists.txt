# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

# C++ to Python bridge, exposing e.g. the Python plugin system to C++.
add_subdirectory(bridge)
# Python C extension module making C++ types usable in Python.
add_subdirectory(cmodule)

# Install OpenAssetIO pure Python into the Python environment.
install(
    DIRECTORY package/openassetio
    DESTINATION "${OPENASSETIO_PYTHON_SITEDIR}"
    FILES_MATCHING PATTERN "*.py"
)


#-----------------------------------------------------------------------
# Install dist-info into the Python environment, to prevent accidental
# overwrite, e.g. pip.

if (OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO)

    file(READ pyproject.toml _pyproject_toml)
    string(REGEX MATCH [[version *= *"([^"]+)"]] _unused "${_pyproject_toml}")
    set(OPENASSETIO_PYTHON_PACKAGE_VERSION ${CMAKE_MATCH_1})
    if (NOT OPENASSETIO_PYTHON_PACKAGE_VERSION)
        message(FATAL_ERROR "Failed to parse version from pyproject.toml")
    endif ()

    set(_dist_info_dir_name openassetio-${OPENASSETIO_PYTHON_PACKAGE_VERSION}.dist-info)

    file(
        COPY
        "${PROJECT_SOURCE_DIR}/cmake/packaging/python.dist-info/INSTALLER"
        "${PROJECT_SOURCE_DIR}/cmake/packaging/python.dist-info/REQUESTED"
        "${PROJECT_SOURCE_DIR}/cmake/packaging/python.dist-info/top_level.txt"
        DESTINATION "${_dist_info_dir_name}"
    )
    configure_file(
        "${PROJECT_SOURCE_DIR}/cmake/packaging/python.dist-info/METADATA.in"
        "${_dist_info_dir_name}/METADATA"
    )
    install(
        DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/${_dist_info_dir_name}"
        DESTINATION "${OPENASSETIO_PYTHON_SITEDIR}"
    )

endif ()

#-----------------------------------------------------------------------
# Tests

if (OPENASSETIO_ENABLE_TESTS)
    add_subdirectory(tests)
endif ()
