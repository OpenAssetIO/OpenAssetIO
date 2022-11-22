#-----------------------------------------------------------------------
# TOML file parser

find_package(tomlplusplus REQUIRED)

#-----------------------------------------------------------------------
# Python

if (OPENASSETIO_ENABLE_PYTHON)
    #-------------------------------------------------------------------
    # Locate packages

    list(APPEND _components Interpreter)
    list(APPEND _components Development.Module)
    if (OPENASSETIO_ENABLE_TESTS)
        list(APPEND _components Development.Embed)
    endif ()

    # Locate the Python package.
    find_package(Python REQUIRED COMPONENTS ${_components})

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
        # Make a naive assumption about a suitable structure under our
        # install-dir. See:
        #   https://discuss.python.org/t/understanding-site-packages-directories/12959
        # We had issues using 'cleverness' to work out the path relative
        # to Python_EXECUTABLE and Python_SITEARCH when symlinks or
        # varying installation structures were used (eg GitHub Actions
        # runners).
        if (WIN32) # Should not use 'bin' for Windows
            set(OPENASSETIO_PYTHON_SITEDIR "Lib/site-packages")
        else ()
            set(OPENASSETIO_PYTHON_SITEDIR
                "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages")
        endif ()
    endif ()

    # pybind11 for C++ Python bindings.
    # TODO(DF): Our pybind11 conan package doesn't give version info, so
    #   we can't pin it at the moment.
    find_package(pybind11 REQUIRED)


    #-------------------------------------------------------------------
    # Locate Python environment

    # Get path to Python executable in the (potentially) created venv.
    if (WIN32)
        set(OPENASSETIO_PYTHON_VENV_EXE "${PROJECT_BINARY_DIR}/test-venv/Scripts/python.exe")
    else ()
        set(OPENASSETIO_PYTHON_VENV_EXE
            "${PROJECT_BINARY_DIR}/test-venv/${CMAKE_INSTALL_BINDIR}/python")
    endif ()

    # Get path to Python executable used for running tests etc.
    if (OPENASSETIO_ENABLE_PYTHON_TEST_VENV)
        set(OPENASSETIO_PYTHON_EXE ${OPENASSETIO_PYTHON_VENV_EXE})
    else ()
        # Use external environment's Python. E.g. this could be a
        # manually `activate`d environment, ideally created using the
        # openassetio-python-venv target.
        set(OPENASSETIO_PYTHON_EXE python)
    endif ()


    #-------------------------------------------------------------------
    # Target to create a Python virtual environment in the install tree.

    # Target to create a Python environment in the install directory.
    # If the venv already exists then this is a no-op.
    add_custom_target(
        openassetio.internal.python-venv.create
        COMMAND ${CMAKE_COMMAND}
        -E echo -- Creating Python environment in ${PROJECT_BINARY_DIR}/test-venv
        COMMAND ${Python_EXECUTABLE} -m venv ${PROJECT_BINARY_DIR}/test-venv
        COMMAND
        ${OPENASSETIO_PYTHON_VENV_EXE} -m pip install --upgrade
        # Pin core packages to give some basic reproducibility across
        # environments.
        setuptools==49.0 pip==22.2.2
    )

    # Add a top-level Python environment creation convenience build
    # target. This target will be augmented via (conditional)
    # `add_dependencies(...)` calls throughout the project, to build up
    # a Python environment appropriate for the enabled components. For
    # example, if tests are enabled then Python test packages will be
    # installed into this environment.
    add_custom_target(openassetio-python-venv)
    add_dependencies(openassetio-python-venv openassetio.internal.python-venv.create)

    # Add Python packages to be installed as a dependency of the
    # top-level Python environment creation convenience target.
    #
    # Also adds Python virtualenv as a build dependency of installing
    # the package(s).
    function(openassetio_add_python_environment_dependency target_name requirements_file_path)
        # Add a `pip install` target to install the Python packages
        # listed in the given requirements.txt into the test venv.
        add_custom_target(
            ${target_name}
            COMMAND
            ${CMAKE_COMMAND} -E echo
            "Installing Python environment dependencies for ${target_name}"
            COMMAND
            ${OPENASSETIO_PYTHON_VENV_EXE} -m pip install --requirement ${requirements_file_path}
        )
        # Python environment must be available to install into.
        add_dependencies(
            ${target_name}
            openassetio.internal.python-venv.create
        )
        # Ensure top-level Python environment creation includes installing
        # these dependencies.
        add_dependencies(
            openassetio-python-venv
            ${target_name}
        )
    endfunction()
endif ()
