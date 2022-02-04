# OpenAssetIO

An open-source interoperability standard for tools and content
management systems used in media production.

OpenAssetIO defines a common set of interactions between a host of the
API (eg: a Digital Content Creation tool or pipeline script) and an
Asset Management System.

It aims to reduce the integration effort and maintenance overhead of
modern CGI pipelines, and pioneer new, standardized asset-centric
workflows in post-production tooling.

OpenAssetIO enabled tools and asset management systems can freely
communicate with each other, without needing to know any specifics of
their respective implementations.

The API has no inherent functionality. It exists as a bridge - at the
boundary between a process that consumes or produces data (the host),
and the systems that provide data coordination and version management
functionality.

## Scope

The API covers the following areas:
 - Resolution of asset references (URIs) into locatable data (URLs).
 - Publishing and retrieval of data for file-based and non-file-based
   assets.
 - Discovery and registration of related assets.
 - Replacement/augmentation of in-application UI elements such as
   browsers and other panels/controls.

The API, by design, does not:
 - Define any standardized data structures for the storage or
   description of assets or
   asset hierarchies.
 - Dictate any aspect of how an asset management system operates,
   organizes, locates or manages asset data and versions.

The API builds upon the production-tested [Katana Asset API](https://learn.foundry.com/katana/4.0/Content/tg/asset_management_system_plugin_api/asset_management_system.html),
addressing several common integration challenges and adding support
for a wider range of asset types and publishing workflows.

## API documentation

The documentation for OpenAssetIO can be found here: [https://thefoundryvisionmongers.github.io/OpenAssetIO](https://thefoundryvisionmongers.github.io/OpenAssetIO/).

## Project status

> **Important:** The project is currently in early beta stage and is
> subject to change. Do not deploy the API in production critical
> situations without careful thought.

We are currently working towards a v1.0.0 release. At present, the API
is sketched in pure `Python`, whilst some structural revisions are being
made. Once the surface area has stabilized, the Core API will be ported
to `C++` with bindings to `Python`.

The code is presented here in its current form to facilitate discussion
and early-adopter testing. We actively encourage engagement in the
[discussion](https://github.com/TheFoundryVisionmongers/OpenAssetIO/discussions)
and to give feedback on current [Issues](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues)
and [Pull Requests](https://github.com/TheFoundryVisionmongers/OpenAssetIO/pulls).

We have been making some structural changes prior to migrating to this
repository, updating from Python 2 to Python 3 and removing some
spurious/legacy concepts. There may well be some rough edges so bear
with us whilst we get things ship-shape.

Please see the [project board](https://github.com/TheFoundryVisionmongers/OpenAssetIO/projects/1)
for work in progress, as well as up-coming topics.

### TODO list
 - Migrate M&E related Entity/Relationship specifications
 - [AR2.0](https://graphics.pixar.com/usd/docs/668045551.html) interop
   investigations
 - Migrate `ManagerPlugin` test harness
 - C++ port of Core API
 - Katana Asset API migration guide/shims
 - `Windows` and `macOS` support

## Background

Within the Media and Entertainment sector, digital content (such as
images, models and editorial data) is usually managed by a central
catalog. This catalog is commonly known as an "Asset Management System",
and forms a singular source of truth for a project.

OpenAssetIO provides an abstraction layer that generalizes the dialog
between a 'host' (eg. a Digital Content Creation application such as
Maya&reg; or Nuke) and one of these systems - a 'manager' (eg. ShotGrid,
ftrack or other proprietary systems).

This project first began in 2013, taking inspiration from the production
tested [Katana Asset API](https://learn.foundry.com/katana/4.0/Content/tg/asset_management_system_plugin_api/asset_management_system.html)
to make it more suitable for a wider variety of uses. Modern pipelines
are incredibly nuanced. Finding a common framework that brings value in
this space is challenging to say the least. Prototypes built during the
development of `OpenAssetIO` over the last few years have demonstrated
significant developer and artist value.

We hope the API forms a practical starting point that addresses many
real-world use cases, and as an industry, we can evolve the standard
over time to support any additional requirements. We are currently
investigating the relationship with [Ar 2.0](https://graphics.pixar.com/usd/docs/668045551.html),
which appears to overlap with a subset of `OpenAssetIO`s concerns.

## Getting started

### System requirements

Ubuntu Linux 20.04 is currently the only fully tested platform. Support
for other platforms is the subject of ongoing work. We further assume
the following system packages are installed

- CMake 3.21+
- GCC 9.3

### Library dependencies

Binary builds additionally require the following packages to be
available to the CMake build system.
- Python 3.9 (development install)
- [pybind11](https://pybind11.readthedocs.io/en/stable/) 2.6.1+

We use the CMake build system for compiling the C++ core library and
its Python bindings. As such, the library dependencies listed above must
be discoverable by CMake's `find_package`.

For reference, during development of OpenAssetIO we use the [conan](https://conan.io/)
package manager, and source the dependencies from the default public
[ConanCenter](https://conan.io/center/) repository. We therefore assume
the presence of CMake build targets as exported by these packages.

> Warning: if attempting to build on CentOS 7 using the ConanCenter
> Python 3.9 package you will likely hit an [issue installing pkgconf](https://github.com/conan-io/conan-center-index/issues/8541).

### Installation

The OpenAssetIO codebase is available as a git repository on GitHub

```shell
git clone git@github.com:TheFoundryVisionmongers/OpenAssetIO
```

### Building

By default, the project will build shared libraries and set the
installation directory to `dist` in the repository root. This can be
overridden by setting the built-in CMake variables `BUILD_SHARED_LIBS`
and `CMAKE_INSTALL_PREFIX`, respectively.

If shared library builds are disabled, then the core library will be
built and installed as a static library, and statically linked into the
Python module.

In order to build and install the binary artifacts, assuming the current
working directory is at the repository root, run

```shell
cmake -S . -B build
cmake --build build
cmake --install build
```

The pure Python component can then be installed into a Python
environment using

```shell
pip install .
```

The pure Python component will not function unless the compiled binary
artifacts are also made available to the Python environment.

### Running tests

Testing is disabled by default and must be enabled by setting the
`OPENASSETIO_ENABLE_TESTS` CMake variable. Assuming that the working
directory is the repository root, we can configure the CMake build as
follows

```shell
cmake -S . -B build -DOPENASSETIO_ENABLE_TESTS=ON
```

#### Quick start: using `ctest`

The manual steps detailed below are conveniently wrapped by CTest -
CMake's built-in test runner. In order to execute the tests,
from the build directory simply run

```shell
ctest
```

This will build and install binary artifacts, create a Python
environment, install the pure Python component and test dependencies,
then execute the tests.

A disadvantage of this is that the pure Python component is
reinstalled every time tests are executed, even if no files changed.

#### Step by step

We must first build and install the binary artifacts. Assuming the CMake
build has been configured as above, then

```shell
cmake --build build
cmake --install build
```

Since the discovered Python may be different from the system Python,
there is a convenience build target to create a Python virtual
environment in the installation directory, which ensures that the same
Python that was linked against is used to create the environment.

```shell
cmake --build build --target openassetio-python-venv
```

We can then use this environment to execute the tests.

Next we must install the pure Python component and test-specific
dependencies. Assuming the install directory is `dist` under the
repository root (the default)

```shell
source dist/bin/activate
pip install .
pip install -r tests/requirements.txt
```

We can now run the Python tests via `pytest`

```shell
pytest tests
```

### Using Vagrant

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
cd ci
vagrant up
# Wait a while...
vagrant ssh
cmake -S openassetio -B build --install-prefix ~/dist \
  --toolchain ~/conan/conan_paths.cmake -DOPENASSETIO_ENABLE_TESTS=ON
```

Then we can run the following steps to build, install and run the tests

```shell
cmake --build build
cmake --install build
cmake --build build --target openassetio-python-venv
source dist/bin/activate
pip install ./openassetio
pip install -r openassetio/tests/requirements.txt
pytest openassetio/tests
```
or alternatively, simply

```shell
cd build
ctest
```

## Getting involved

- See the [contribution guide](contributing/PROCESS.md)

> Maya&reg;, is a registered trademark of Autodesk, Inc., and/or its
> subsidiaries and/or affiliates in the USA and/or other countries.
