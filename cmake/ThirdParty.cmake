#-----------------------------------------------------------------------
# Python

if (OPENASSETIO_ENABLE_PYTHON)
    #-------------------------------------------------------------------
    # Locate packages

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
    # Locate Python environment in build/install tree.

    # Directory where downloaded Python packages should be stored.
    set(OPENASSETIO_PYTHON_DEPENDENCIES_DIR "${PROJECT_BINARY_DIR}/dependencies/python")

    # Get path to Python executable in the created venv, and a way to activate
    # the venv itself.
    if (WIN32)
        set(OPENASSETIO_PYTHON_VENV_ACTIVATE "${CMAKE_INSTALL_PREFIX}/Scripts/activate.bat")
        set(OPENASSETIO_PYTHON_VENV_EXE "${CMAKE_INSTALL_PREFIX}/Scripts/python.exe")
    else ()
        set(OPENASSETIO_PYTHON_VENV_ACTIVATE
            . "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/activate")
        set(OPENASSETIO_PYTHON_VENV_EXE "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/python")
    endif ()


    #-------------------------------------------------------------------
    # `pip` target creation functions

    # Download (but don't install) Python packages.
    #
    # Downloading packages once, and then using `--find-links` when
    # installing, allows devs to more easily work offline.
    function (openassetio_add_pip_download_target target_name description)
        add_custom_target(
            ${target_name}
            COMMAND ${CMAKE_COMMAND} -E echo -- "${description}"
            COMMAND
            ${Python_EXECUTABLE} -m pip download
            --retries 0 --timeout ${OPENASSETIO_PYTHON_PIP_TIMEOUT}
            --find-links ${OPENASSETIO_PYTHON_DEPENDENCIES_DIR}
            --destination-directory ${OPENASSETIO_PYTHON_DEPENDENCIES_DIR}
            ${ARGN}
        )
    endfunction()

    # Install Python package from cached package download directory.
    function (openassetio_add_pip_install_target target_name description)
        add_custom_target(
            ${target_name}
            COMMAND ${CMAKE_COMMAND} -E echo -- ${description}
            COMMAND
            ${OPENASSETIO_PYTHON_VENV_EXE} -m pip install
            # For speed, build from the venv rather than copying the
            # whole project to a temporary environment. Note that this
            # is a pip feature, setuptools also has its own build cache
            # (see setup.cfg). This flag roughly halves test runtime.
            --no-build-isolation
            --no-index --find-links ${OPENASSETIO_PYTHON_DEPENDENCIES_DIR}
            ${ARGN}
        )
    endfunction()


    #-------------------------------------------------------------------
    # Target to create a Python virtual environment in the install tree.

    # Download core setuptools dependencies so we don't always need an
    # online connection to local install OpenAssetIO. Need to cache the
    # build tools explicitly due to build isolation, see:
    # https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#build-process
    # This also includes runtime dependencies of packages in the
    # resources directory, whose install will otherwise fail due to
    # --no-index.
    openassetio_add_pip_download_target(
        openassetio.internal.python-venv.download-deps
        "Downloading core Python libraries"
        wheel==0.37.1 setuptools==49.0
        # We must upgrade pip so that the build directory is not
        # copied to a temporary directory, since doing so could cause
        # Windows to fail with permissions errors when concurrently
        # installing Python packages and building the C++ component.
        pip==22.2.2
    )

    # Target to create a Python environment in the install directory.
    # If the venv already exists then this is a no-op.
    # Requires: openassetio.internal.python-venv.download-deps
    add_custom_target(
        openassetio.internal.python-venv.create
        COMMAND ${CMAKE_COMMAND} -E echo -- Creating Python environment in ${CMAKE_INSTALL_PREFIX}
        COMMAND ${Python_EXECUTABLE} -m venv ${CMAKE_INSTALL_PREFIX}
        # Install `wheel` so that setuptools can build OpenAssetIO.
        COMMAND
        ${OPENASSETIO_PYTHON_VENV_EXE} -m pip install --upgrade
        --no-index --find-links ${OPENASSETIO_PYTHON_DEPENDENCIES_DIR}
        wheel setuptools pip
    )

    # Combine Python venv download and create steps into a single
    # convenience target.
    add_custom_target(
        openassetio-python-venv
        COMMAND
        ${CMAKE_COMMAND} --build ${PROJECT_BINARY_DIR}
        --target
        openassetio.internal.python-venv.download-deps
        COMMAND
        ${CMAKE_COMMAND} --build ${PROJECT_BINARY_DIR}
        --target
        openassetio.internal.python-venv.create
    )
endif ()
