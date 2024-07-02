# SimpleCppManager

A simple C++ manager and plugin useful in basic host application test
cases, where a C++ plugin is required.

Where Python is available, it is recommended to use the [Basic Asset
Library](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL) fake
manager for testing, which is much more configurable and supports a
wider cross-section of the OpenAssetIO API.

The SimpleCppManager manager/plugin only implements the minimal required
methods plus `resolve`. It is entirely configured by the settings
provided at `initialize` time (typically coming from the standard
OpenAssetIO `.toml` configuration file). This includes the "database" of
entities, encoded as a CSV document in a string setting.

## Building

### As part of OpenAssetIO

The plugin can be built and installed as part of OpenAssetIO by setting
the CMake option `OPENASSETIO_ENABLE_SIMPLECPPMANAGER=ON` when building
OpenAssetIO.

### Independently

Alternatively, the plugin can be built as an independent CMake project.

Available CMake settings
- `OPENASSETIO_GLIBCXX_USE_CXX11_ABI` - If truthy, and using
  `libstdc++` (default on Linux), the C++11 ABI will be used rather than
  the deprecated pre-C++11 ABI. The value of this option must match the
  identically named option used when building OpenAssetIO. See
  [VFX Reference Platform](https://vfxplatform.com/).
- `OPENASSETIO_ENABLE_TESTS` - If truthy, tests will be enabled. These
  require an OpenAssetIO build with Python enabled, and a Python
  environment with `pytest` installed.

Assuming the working directory is at the root of the SimpleCppManager
project, and assuming a POSIX host
```sh
export CMAKE_PREFIX_PATH=/path/to/OpenAssetIO/dist
cmake -S . -B build -DOPENASSETIO_GLIBCXX_USE_CXX11_ABI=OFF
cmake --build build --parallel
cmake --install build --prefix /path/to/OpenAssetIO/plugins
```
where `/path/to/OpenAssetIO/plugins` is an arbitrary path to be provided
in the `OPENASSETIO_PLUGIN_PATH` environment variable.

## Usage

See [example config file](tests/resources/openassetio_config.toml) for
available configuration options, including constructing a database of
`resolve`able entities.

Once the plugin has been installed, the usual configuration via
`OPENASSETIO_PLUGIN_PATH` and `OPENASSETIO_DEFAULT_CONFIG` can be used
(see API documentation).




