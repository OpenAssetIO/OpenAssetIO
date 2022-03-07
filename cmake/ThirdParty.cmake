#-----------------------------------------------------------------------
# Python

if (OPENASSETIO_ENABLE_PYTHON)

    # Components required for building a Python module.
    list(APPEND python_components Development.Module)
    list(APPEND python_components Interpreter)

    # Locate the Python package.
    find_package(
        Python ${OPENASSETIO_PYTHON_VERSION}
        REQUIRED
        COMPONENTS ${python_components})

    # Debug log some outputs expected from the built-in FindPython.
    message(TRACE "Python_EXECUTABLE = ${Python_EXECUTABLE}")
    message(TRACE "Python_INTERPRETER_ID = ${Python_INTERPRETER_ID}")
    message(TRACE "Python_STDLIB = ${Python_STDLIB}")
    message(TRACE "Python_STDARCH = ${Python_STDARCH}")
    message(TRACE "Python_SITELIB = ${Python_SITELIB}")
    message(TRACE "Python_SITEARCH = ${Python_SITEARCH}")
    message(TRACE "Python_SOABI = ${Python_SOABI}")
    message(TRACE "Python_INCLUDE_DIRS = ${Python_INCLUDE_DIRS}")
    message(TRACE "Python_LINK_OPTIONS = ${Python_LINK_OPTIONS}")
    message(TRACE "Python_LIBRARIES = ${Python_LIBRARIES}")
    message(TRACE "Python_LIBRARY_DIRS = ${Python_LIBRARY_DIRS}")
    message(TRACE "Python_RUNTIME_LIBRARY_DIRS = ${Python_RUNTIME_LIBRARY_DIRS}")
    message(TRACE "Python_VERSION = ${Python_VERSION}")
    message(TRACE "Python_VERSION_MAJOR = ${Python_VERSION_MAJOR}")
    message(TRACE "Python_VERSION_MINOR = ${Python_VERSION_MINOR}")
    message(TRACE "Python_VERSION_PATCH = ${Python_VERSION_PATCH}")

    if (OPENASSETIO_PYTHON_SITEDIR STREQUAL "")
        # Default to mirroring the Python distribution's structure.
        get_filename_component(python_bin_dir ${Python_EXECUTABLE} DIRECTORY)
        file(RELATIVE_PATH python_site_dir_rel_to_bin ${python_bin_dir} ${Python_SITEARCH})
        if (NOT CMAKE_INSTALL_BINDIR OR WIN32) # Should not use 'bin' for Windows
            set(bin_dir .)
        else ()
            set(bin_dir "${CMAKE_INSTALL_BINDIR}")
        endif ()
        # Relative path from install root to site-packages.
        cmake_path(SET OPENASSETIO_PYTHON_SITEDIR NORMALIZE "${bin_dir}/${python_site_dir_rel_to_bin}")
    endif ()

    # pybind11 for C++ Python bindings.
    # TODO(DF): Our pybind11 conan package doesn't give version info, so
    #   we can't pin it at the moment.
    find_package(pybind11 REQUIRED)
endif ()
