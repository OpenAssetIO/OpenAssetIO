# Building OpenAssetIO

## System requirements

We assume the following system packages are installed

- CMake 3.21+
- GCC 9.3

For linting and other build verification options, we assume the
following packages are installed:

- LLVM 12.0.0

## Library dependencies

Binary builds additionally require the following packages to be
available to the CMake build system.
- Python 3.9 (development install)
- [pybind11](https://pybind11.readthedocs.io/en/stable/) 2.6.1+

Building and running tests requires the following additional packages:

- catch2 2.13
- trompeloeil 42

We use the CMake build system for compiling the C++ core library and
its Python bindings. As such, the library dependencies listed above must
be discoverable by CMake's `find_package`.

For reference, during development of OpenAssetIO we use the [conan](https://conan.io/)
package manager, and source the dependencies from the default public
[ConanCenter](https://conan.io/center/) repository. We therefore assume
the presence of CMake build targets as exported by these packages.

> Warning: if attempting to build on CentOS 7 using the ConanCenter
> Python 3.9 package you will likely hit an [issue installing pkgconf](https://github.com/conan-io/conan-center-index/issues/8541).

> Warning: On macOS, by default, CMake prefers Framework installations
> (see: [$CMAKE_FIND_FRAMEWORK](https://cmake.org/cmake/help/latest/variable/CMAKE_FIND_FRAMEWORK.html)).
> This means dependencies such as Python may default to the system
> installation despite alternatives being present. In addition, if you
> are attempting to use the ConanCenter cpython package as an
> alternative, we have encountered missing header issues that may
> require additional work/configuration to resolve.

## Building

We use the CMake build system for compiling the C++ core library and
its Python bindings.

By default, the project will build shared libraries and set the
installation directory to `dist` under the build directory. This can be
overridden by setting the built-in CMake variables `BUILD_SHARED_LIBS`
and `CMAKE_INSTALL_PREFIX`, respectively.

If shared library builds are disabled, then the core library will be
built and installed as a static library, and statically linked into the
Python module.

In order to build and install the binary artifacts and Python sources,
assuming the current working directory is at the repository root, run

```shell
cmake -S . -B build
cmake --build build
cmake --install build
```

The generated install tree can then be used directly (e.g. by extending
`PYTHONPATH` and/or `LD_LIBRARY_PATH`), or as the source for a further
packaging step.

Note that the `openassetio` Python package will not function unless the
binary artifacts are also made available to your Python environment.

## Running tests

Testing is disabled by default and must be enabled by setting the
`OPENASSETIO_ENABLE_TESTS` CMake variable.

In addition, test fixtures are configured such that a Python environment
is created during the test run. This can be disabled by setting
`OPENASSETIO_ENABLE_PYTHON_TEST_VENV` to `OFF`. If this is `OFF` then
you must ensure test dependencies are installed.

Assuming that the working directory is the repository root, we can
configure the CMake build as follows

```shell
cmake -S . -B build -DOPENASSETIO_ENABLE_TESTS=ON
```

### Using `ctest`

The steps required to bootstrap an environment and execute the tests are
conveniently wrapped by CTest - CMake's built-in test runner. In order
to execute the tests, from the `build` directory simply run

```shell
ctest
```

This will build and install binary artifacts and Python sources, create
a Python environment, install test dependencies, then execute the tests.

## Using Vagrant

Included for convenience is a [Vagrant](https://www.vagrantup.com/)
configuration for creating reproducible build environments. This is
configured to create a virtual machine that matches the Linux Github CI
environment as close as is feasible.

The Vagrant VM installs third-party library dependencies using the
[conan](https://conan.io/) package manager, and sources the dependencies
from the default public [ConanCenter](https://conan.io/center/)
repository.

In order to build and run the tests within a Vagrant VM, assuming
Vagrant is installed and the current working directory is the root of
the repository, run the following

```shell
cd resources/build
vagrant up
# Wait a while...
vagrant ssh
cmake -S openassetio -B build --install-prefix ~/dist \
  --toolchain ~/.conan/conan_paths.cmake
```

Then we can run the usual steps (see above) to build and install
OpenAssetIO, and run the tests (if enabled).

## CMake presets

We include several CMake presets for common build configurations. We
recommend the `dev` preset be used for day-to-day development on the
project. The `test` preset provides comprehensive coverage of all
components.
