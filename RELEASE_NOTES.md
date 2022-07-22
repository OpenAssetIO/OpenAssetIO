Release Notes
=============

v1.0.0-alpha.X
--------------

### Breaking changes

- Redesigned the manager initialization workflow, such that
  `ManagerInterface`/`Manager.setSettings` and `initialize` are no
  longer independent calls. Specifically, `setSettings` is removed and
  `initialize` now takes settings as an argument. This also entailed
  renaming `ManagerInterface`/`Manager.getSettings` to `settings`.
  [#503](https://github.com/OpenAssetIO/OpenAssetIO/issues/503)

- Redesigned `managementPolicy` to return a `TraitsData` rather than a
  bitfield for specifying the policy of the manager for a given trait
  set. This deprecated the `managementPolicy` constants, which have been
  removed.
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)

- Removed thumbnail support from the core API and updated docs to make
  use of an imagined `WantsThumbnailTrait` policy trait, since this is
  an industry-specific feature.
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)

- Renamed the manager/host namespaces to `managerApi` and `hostApi` for
  consistency with the rest of the codebase.
  [#457](https://github.com/OpenAssetIO/OpenAssetIO/issues/457)

- Renamed both `ManagerFactoryInterface` as well as the subclass
  `PluginSystemManagerFactory` to `ManagerInterfaceFactoryInterface`
  and `PluginSystemManagerInterfaceFactory`, respectively, to avoid
  potential ambiguity. I.e. that they instantiate instances of
  `ManagerInterface` rather than `Manager`.
  [#506](https://github.com/OpenAssetIO/OpenAssetIO/issues/506)

- Renamed the `LoggerInterface` constant `kDebugAPI` to `kDebugApi`.
  [#457](https://github.com/OpenAssetIO/OpenAssetIO/issues/457)

- Removed the `LoggerInterface.progress()` method as it requires some
  careful thought how best to implement, and in the meantime is unused
  and only complicates the C++ migration.
  [#504](https://github.com/OpenAssetIO/OpenAssetIO/issues/504)

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

- Removed `Session.host()` as it is not useful for foreseeable workflows
  (beyond tests). Note that `HostSession.host()` remains.
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)

- Removed the Transactions API, including the `ManagerInterface`
  methods, and `TransactionCoordinator` helpers.
  [#421](https://github.com/OpenAssetIO/OpenAssetIO/issues/421)

- Removed the `Session` methods `createContext`, `freezeContext` and
  `thawContext`.
  [#430](https://github.com/OpenAssetIO/OpenAssetIO/issues/430)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)

- Added `createContext`, `createChildContext`,
  `persistenceTokenForContext` and `contextFromPersistenceToken` methods
  to the `Manager` class to facilitate context creation and the
  serialization of a manager's state for persistence or distribution.
  [#421](https://github.com/OpenAssetIO/OpenAssetIO/issues/421),
  [#430](https://github.com/OpenAssetIO/OpenAssetIO/issues/430)
  [#452](https://github.com/OpenAssetIO/OpenAssetIO/issues/452)

- Renamed the `ManagerInterface` methods `freezeState` and `thawState`
  to `persistenceTokenForState` and `stateFromPersistenceToken` to
  better describe their behavior.
  [#452](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)

- Marked `Host` class as `final` in both Python and C++ and so it cannot
  be subclassed.
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)

- Removed `Context.managerOptions`.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)

- Renamed `Context.managerInterfaceState` to `Context.managerState`.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)

- Changed `Context.kOther` to `kUnknown`, and changed the default
  context access to `kUnknown`. This better describes its use, and
  encourages hosts to properly configure the context before use.

- Changed `Context` access and retention constants to `enum`s in C++
  that are bound to Python as opaque instances (via `pybind11::enum_`),
  rather than strings and integers, respectively.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)

- Split `ManagerInterface::createState` into `createState` and
  `createChildState` to more explicitly state intent, and simplify
  language bindings.
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)

- Ammended the behaviour of `ManagerInterface` such that derived classes
  who implement the `createState` method _must_ also implement
  `createChildState`, `persistenceTokenForState` and
  `stateFromPersistenceToken`. Checks have been added to the
  `openassetio.test.manager` `apiComplianceSuite` to validate manager
  implementations agains this requirement.

- Made the constructors of the following classes private: `Context`,
  `Host`, `HostSession`, `Manager`, `TraitsData`. The static `make`
  methods should be used to construct new instances.
  [#481](https://github.com/OpenAssetIO/OpenAssetIO/issues/481)

- Removed the `makeShared` pointer factory. The per-class static `make`
  methods should be used instead.
  [#481](https://github.com/OpenAssetIO/OpenAssetIO/issues/481)


### Improvements

- Added `ManagerInterfaceState` abstract base class, that should be
  used as a base for all instances returned from
  `ManagerInterface::createState()`.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)

- Added short-form macros for C API symbols, so that, for example,
  `oa_symbolName` can be used instead of wrapping every reference in the
  namespacing macro, i.e. `OPENASSETIO_NS(symbolName)`.
  [#370](https://github.com/OpenAssetIO/OpenAssetIO/issues/370)

- Migrated the following classes to C++: `Context`, `Host`,
  `HostInterface`, `HostSession` and `LoggerInterface`,
  `ManagerInterfaceFactoryInterface`. Debug and audit functionality is
  left for future work.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#504](https://github.com/OpenAssetIO/OpenAssetIO/issues/504)
  [#507](https://github.com/OpenAssetIO/OpenAssetIO/issues/507)

- Migrated the following `ManagerInterface` methods to C++
  `initialize`, `managementPolicy`, `createState`, `createChildState`,
  `persistenceTokenForState`, `stateFromPersistenceToken`.
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)

- Migrated the following `Manager` methods to C++ `initialize`
  `managementPolicy`, `createContext`, `createChildContext`,
  `persistenceTokenForContext`, `contextFromPersistenceToken`.
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)

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

- Added support for customisable `managementPolicy` responses to
  the `BasicAssetLibrary` example/test manager. See:
    `resources/examples/manager/BasicAssetLibrary/schema.json`
  [#459](https://github.com/OpenAssetIO/OpenAssetIO/issues/459)


### Bug fixes

- Python objects that inherit from a C++ base class, and are held by a
  C++ object as a C++ base class pointer, will no longer be destroyed
  prematurely.
  See [pybind/1333](https://github.com/pybind/pybind11/issues/1333).
  [#523](https://github.com/OpenAssetIO/OpenAssetIO/pull/523)

- The CMake `clean` target no longer breaks subsequent builds, including
  offline builds.
  [#311](https://github.com/OpenAssetIO/OpenAssetIO/issues/311)

- C headers are now C99 compliant. In particular, they no longer
  `#include` C++-specific headers.
  [#337](https://github.com/OpenAssetIO/OpenAssetIO/issues/337)


v1.0.0-alpha.1
--------------

Initial alpha release.
