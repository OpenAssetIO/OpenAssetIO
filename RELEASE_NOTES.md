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

- Switched the C/C++ symbol namespace to use a separate ABI version.
  The version is defined by the major version component of the last
  release in which the ABI changed.
  [#377](https://github.com/OpenAssetIO/OpenAssetIO/issues/377)

- Renamed the following trait related types and variables to better
  align with the concepts of the API:
  [#340](https://github.com/OpenAssetIO/OpenAssetIO/issues/340)
  - `SpecificationBase.kTraitIds` to `kTraitSet`.
  - `TraitsData::TraitIds` to `TraitSet`
  - `TraitsData::traitIds()` to `traitSet()`

- Removed the Transactions API, including the `ManagerInterface`
  methods, and `TransactionCoordinator` helpers. Added `freezeContext`
  and `thawContext` methods to the `Session` class to allow
  serialization of a manager's state for persistence or distribution.
  [#421](https://github.com/OpenAssetIO/OpenAssetIO/issues/421)

- Removed `Session.host()` as it is not useful for foreseeable workflows
  (beyond tests). Note that `HostSession.host()` remains.
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)

- Marked `Host` class as `final` in both Python and C++ and so it cannot
  be subclassed.
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)


### Improvements

- Added short-form macros for C API symbols, so that, for example,
  `oa_symbolName` can be used instead of wrapping every reference in the
  namespacing macro, i.e. `OPENASSETIO_NS(symbolName)`.
  [#370](https://github.com/OpenAssetIO/OpenAssetIO/issues/370)

- `Host` and `HostInterface` classes have been migrated to C++.
  Debug and audit functionality is left for future work.
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/370)

- Switched to preferring un-versioned `clang-tidy` executables when
  the `OPENASSETIO_ENABLE_CLANG_TIDY` build option is enabled. We
  currently target LLVM v12, earlier or later versions may yield
  new or false-positive warnings.
  [#392](https://github.com/OpenAssetIO/OpenAssetIO/issues/392)

- Added CMake presets for development and testing.
  [#315](https://github.com/OpenAssetIO/OpenAssetIO/issues/315)

- Added `OPENASSETIO_PYTHON_PIP_TIMEOUT` CMake cache variable to allow
  customising `pip install` socket timeout. Useful if working offline
  with dependencies already downloaded.
  [#407](https://github.com/OpenAssetIO/OpenAssetIO/issues/407)

- Updated the machine image bootstrap scripts in `resources/build` to
  use the `$WORKSPACE` env var instead of `$GITHUB_WORKSPACE` to
  determine the root of a checkout when configuring the environment.

- Added `resources/build/requirements.txt` covering build toolchain
  requirements.

- Bumped conan version installed by bootstrap scripts to `1.48.1`
  [#401](https://github.com/OpenAssetIO/OpenAssetIO/issues/401)

- Updated the Ubuntu bootstrap script to ensure `clang-format` and
  `clang-tidy` use the v12 alternatives.


### Bug fixes

- The CMake `clean` target no longer breaks subsequent builds, including
  offline builds.
  [#311](https://github.com/OpenAssetIO/OpenAssetIO/issues/311)

- C headers are now C99 compliant. In particular, they no longer
  `#include` C++-specific headers.
  [#337](https://github.com/OpenAssetIO/OpenAssetIO/issues/337)


v1.0.0-alpha.1
--------------

Initial alpha release.
