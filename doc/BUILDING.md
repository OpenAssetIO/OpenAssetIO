# Building OpenAssetIO

## Contents

- [System requirements](#system-requirements)
- [Library dependencies](#library-dependencies)
  - [Build dependencies](#build-dependencies)
  - [Test dependencies](#test-dependencies)
- [Building](#building)
  - [Building via pip](#building-via-pip)
  - [Sandboxed builds](#sandboxed-builds)
- [CMake options](#cmake-options)
  - [Presets](#presets)
- [Running tests](#running-tests)
  - [Using `ctest`](#using-ctest)

## System requirements

We assume the following system packages are installed

- CMake 3.27+
- C++17 or later compliant compiler
(GCC 9.3+ / MSVC 16.9+ / macOS 10.15+)

For linting and other build verification options, we assume the
following packages are installed:

- LLVM 12.0.0

## Library dependencies

### Build dependencies

Binary builds additionally require the following packages to be
available.

- [Python 3.9+](https://www.python.org/) (development install)
- [pybind11](https://pybind11.readthedocs.io/en/stable/) 2.8.1+
- [toml++](https://marzer.github.io/tomlplusplus/) 3.2.0+
- [fmt](https://github.com/fmtlib/fmt) 9.1.0
- [Ada](https://github.com/ada-url/ada) 2.7.4
- [PCRE2](https://github.com/PCRE2Project/pcre2) 10.42
- [pybind11-stubgen](https://github.com/sizmailov/pybind11-stubgen)
  2.5.1 (optional, enabled by default)

### Test dependencies

Building and running tests requires the following additional packages:

- [catch2](https://github.com/catchorg/Catch2/) 2.13
- [trompeloeil](https://github.com/rollbear/trompeloeil) 42

We use the CMake build system for compiling the C++ core library and
its Python bindings. As such, a library being available means that it
must be discoverable by CMake's [`find_package`](https://cmake.org/cmake/help/latest/command/find_package.html).

During development, we tend use [ConanCenter](https://conan.io/center/)
to fulfill the [`find_package`](https://cmake.org/cmake/help/latest/command/find_package.html) requirement.
See [Building](#building) for more information.

## Building

OpenAssetIO consists of a core C++ project, as well as a set of C and
Python bindings to that core library. These modules are organized into a
CMake project, and are all built together by default.

Assuming your build environment has the required dependencies,
[(see above)](#build-dependencies), OpenAssetIO can be built and installed by
running:

```shell
cmake -S . -B build
cmake --build build
cmake --install build
```

> **Note**
>
> A common error to encounter is to find that CMake cannot resolve
> its dependencies via [`find_package`](https://cmake.org/cmake/help/latest/command/find_package.html)
>
> A convenient way to solve this is to use the [`CMAKE_TOOLCHAIN_FILE`](https://cmake.org/cmake/help/v3.24/envvar/CMAKE_TOOLCHAIN_FILE.html)
> environment variable to augment CMake's package search paths.
>
> For example, to use [`conan`](https://docs.conan.io/en/1.46/installation.html)
> to resolve dependencies (as we do during internal development), run
> the following commands from the root of the repository prior to
> building:
>
> ```shell
> conan install -if .conan resources/build --build=missing
> export CMAKE_TOOLCHAIN_FILE=`pwd`/.conan/conan_paths.cmake
> ```
>
> (These commands assume a Linux host, translate as necessary).
>
> This installs OpenAssetIO's dependencies as described in
> `/resources/build/conanfile.py`, and allows CMake to deduce the
> locations via referencing the generated `conan_paths.cmake`. Note that
> this does not include a development install of Python, which should
> be provided by other means.

The artifacts are installed to `/build/dist`. This default location can
be overridden by setting `CMAKE_INSTALL_PREFIX` prior to build.

By default, OpenAssetIO builds as a shared library.

> **Warning**
>
> It is strongly recommended that OpenAssetIO is built as a shared
> library, to ensure that OpenAssetIO C++ manager plugins can load
> correctly.

If shared library builds are disabled, then the core library will
be built and installed as a static library, and statically linked into
the Python module.

In installing the Python module, OpenAssetIO creates a valid Python
package, placed at
`build/dist/lib/{python-version}/site-packages/openassetio`.

### Building via pip

OpenAssetIO can alternately be built and installed via `pip`, which may
be preferable to the exclusively Python focused developer. Check out the
repository, and from the root, run:

```shell
python -m pip install src/openassetio-python
```

This will automatically build and install the Python extension module
into your python environment, along with the Python sources. After this,
you should be able to simply `import openassetio` from your python shell.

### Sandboxed builds

For a more convenient "out of the box" build environments, OpenAssetIO
also provides several sandboxed build environments, which you can read
about [here](SANDBOXED_BUILDS.md).

## CMake options

OpenAssetIO provides several custom CMake options to control the
behaviour of the build.

| Option                                            | Description                                                           | Default |
|---------------------------------------------------|-----------------------------------------------------------------------|---------|
| `OPENASSETIO_ENABLE_PYTHON`                       | Additionally build python bindings                                    | `ON`    |
| `OPENASSETIO_PYTHON_SITEDIR`                      | Python site-packages install prefix subdirectory                      | auto    |
| `OPENASSETIO_ENABLE_PYTHON_STUBGEN`               | Enable Python .pyi stub file generation                               | `ON`    |
| `OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO`     | Create a dist-info metadata directory alongside Python installation   | `ON`    |
| `OPENASSETIO_ENABLE_SIMPLECPPMANAGER`             | Build the SimpleCppManager example plugin                             | `OFF`   |
| `OPENASSETIO_ENABLE_TESTS`                        | Additionally build tests                                              | `OFF`   |
| `OPENASSETIO_ENABLE_PYTHON_TEST_VENV`             | Automatically create environment when running tests                   | `ON`    |
| `OPENASSETIO_WARNINGS_AS_ERRORS`                  | Treat compiler warnings as errors                                     | `OFF`   |
| `OPENASSETIO_ENABLE_IPO`                          | Enable Interprocedural Optimization, aka Link Time Optimization (LTO) | `ON`    |
| `OPENASSETIO_ENABLE_POSITION_INDEPENDENT_CODE`    | Enable position independent code for static library builds            | `ON`    |
| `OPENASSETIO_ENABLE_NEW_DTAGS`                    | Set RUNPATH, overriding RPATH, on linux platforms                     | `OFF`   |
| `OPENASSETIO_ENABLE_SANITIZER_ADDRESS`            | Enable address sanitizer                                              | `OFF`   |
| `OPENASSETIO_ENABLE_SANITIZER_LEAK`               | Enable leak sanitizer                                                 | `OFF`   |
| `OPENASSETIO_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR` | Enable undefined behavior sanitizer                                   | `OFF`   |
| `OPENASSETIO_ENABLE_SANITIZER_THREAD`             | Enable thread sanitizer                                               | `OFF`   |
| `OPENASSETIO_ENABLE_SANITIZER_MEMORY`             | Enable memory sanitizer                                               | `OFF`   |
| `OPENASSETIO_ENABLE_GLIBCXX_DEBUG`                | Enable libstdc++ debug mode                                           | `OFF`   |
| `OPENASSETIO_ENABLE_CLANG_TIDY`                   | Enable clang-tidy analysis during build                               | `OFF`   |
| `OPENASSETIO_ENABLE_CPPLINT`                      | Enable cpplint linter during build                                    | `OFF`   |
| `OPENASSETIO_ENABLE_CMAKE_LINT`                   | Enable cmake-lint linter during build                                 | `OFF`   |

### Presets

To avoid managing these configuration variables manually, we include
several CMake [presets](https://github.com/OpenAssetIO/OpenAssetIO/blob/main/CMakePresets.json)
for common build configurations.
We recommend the `dev` preset be used for day-to-day development, whilst
the `test` preset provides comprehensive coverage of all components.

## Running tests

Testing is disabled by default and must be enabled by setting the
`OPENASSETIO_ENABLE_TESTS` CMake variable.

In addition, test fixtures are configured such that a Python environment
is created during the test run. This can be disabled by setting
`OPENASSETIO_ENABLE_PYTHON_TEST_VENV` to `OFF`. If this is `OFF` then
you must ensure the additional [test dependencies](#test-dependencies)
are installed manually.

Assuming that the working directory is the repository root, we can
configure the CMake build as follows

```shell
cmake -S . -B build -DOPENASSETIO_ENABLE_TESTS=ON
```

### Using `ctest`

The steps required to bootstrap an environment and execute the tests are
conveniently wrapped by CTest - CMake's built-in test runner. In order
to execute the tests, from the root of the repository run

```shell
ctest --test-dir build
```

This will build and install binary artifacts and Python sources, create
a Python environment, install test dependencies, then execute the tests.
