Release Notes
=============

v1.0.0-alpha.X
--------------

### Breaking changes

- Split `Specification` class into `SpecificationBase` and `TraitsData`
  This properly defines the separation of the generic data container
  from the strongly typed views used to get/set well known traits and
  their properties.
  [#348](https://github.com/OpenAssetIO/OpenAssetIO/issues/348)

### Bug fixes

- C headers are now C99 compliant. In particular, they no longer 
  `#include` C++-specific headers. 
  [#337](https://github.com/OpenAssetIO/OpenAssetIO/issues/337)


### Improvements

- Switched to preferring un-versioned `clang-tidy` executables when
  the `OPENASSETIO_ENABLE_CLANG_TIDY` build option is enabled. We
  currently target LLVM v12, earlier or later versions may yield
  new or false-positive warnings.
  [#392](https://github.com/OpenAssetIO/OpenAssetIO/issues/392)

- Added CMake presets for development and testing.
  [#315](https://github.com/OpenAssetIO/OpenAssetIO/issues/315)

- Updated the machine image bootstrap scripts in `resources/build` to
  use the `$WORKSPACE` env var instead of `$GITHUB_WORKSPACE` to
  determine the root of a checkout when configuring the environment.

- Added `resources/build/requirements.txt` covering build toolchain
  requirements.

- Bumped conan version installed by bootstrap scripts to `1.48.1`
  [#401](https://github.com/OpenAssetIO/OpenAssetIO/issues/401)


### Bug fixes

- The CMake `clean` target no longer breaks subsequent builds, including
  offline builds.
  [#311](https://github.com/OpenAssetIO/OpenAssetIO/issues/311)


v1.0.0-alpha.1
--------------

Initial alpha release.
