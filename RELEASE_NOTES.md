Release Notes
=============

v1.0.0-alpha.x
--------------

### Breaking changes

- The `PythonPluginSystem` no longer clears existing plugin
  registrations when `scan` is called. The
  `PythonPluginSystemManagerImplementationFactory` has been updated to
  call `reset` itself, so this change only affects any direct use of the
  `PythonPluginSystem` by third party code.
  [#703](https://github.com/OpenAssetIO/OpenAssetIO/issues/703)

- Removed references to `openassetio-traitgen` from codebase, is now in
  [own repository](https://github.com/OpenAssetIO/OpenAssetIO-TraitGen)
  [#715](https://github.com/OpenAssetIO/OpenAssetIO/issues/715)

- Removed `toml++` as vendored library. Is now an external dependency
  similar to other external dependencies.

- Moved `setup.py` and `pyproject.toml` under the Python component's
  directory, i.e. `src/openassetio-python`. This means the minimum
  version of `pip` used to build wheels (or install from source) is now
  21.3, where in-tree builds are the default.
  [#728](https://github.com/OpenAssetIO/OpenAssetIO/issues/728)

- Updated various Python method argument names to match their C++
  equivalent. Specifically this affects
  `Manager`/`ManagerInterface.managementPolicy`,
  `SeverityFilter.setSeverity`, `TraitsData.hasTrait` / `.addTrait` /
  `.addTraits` / `.setTraitProperty` / `.getTraitProperty` /
  `.traitPropertyKeys` / copy-constructor.
  [#743](https://github.com/OpenAssetIO/OpenAssetIO/issues/743)


### Improvements

- Added `openassetio-build` docker image. This is an extension of the
  already used [ASFW CY22 docker image](https://hub.docker.com/r/aswf/ci-base/tags?name=2022),
  but with the additional openassetio dependencies installed into it.
  As we have also installed test dependencies into this image, this
  unlocks out-of-the-box sandboxed testing workflows via docker.


v1.0.0-alpha.6
--------------

### Breaking changes

- Renamed the `Trait` Python class to `TraitBase` for
  consistency with other classes.
  [#703](https://github.com/OpenAssetIO/OpenAssetIO/issues/703)

- Renamed the `openassetio-codegen` tool to `openassetio-traitgen` to
  avoid ambiguity.
  [#646](https://github.com/OpenAssetIO/OpenAssetIO/issues/646)

- The BasicAssetLibrary test-harness manager plugin has been extracted
  into its [own repository](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL)
  to simplify its ongoing development and version management.
  [#672](https://github.com/OpenAssetIO/OpenAssetIO/issues/672)

### Improvements

- Added compatibility with Python 3.7.
  [#660](https://github.com/OpenAssetIO/OpenAssetIO/issues/660)


v1.0.0-alpha.5
--------------

### Breaking changes

- Added `[[nodiscard]]` attribute to various `make` factory functions,
  may generate additional compiler warnings in your project.

- Removed predownload of test dependencies, meaning contributors must
  reuse their python environments in order to run tests offline.
  [#629](https://github.com/OpenAssetIO/OpenAssetIO/issues/629)

- Changed location of python virtual environment created by
  `openassetio-python-venv` CMake build target to be outside of the
  CMake install tree. This target is executed during test runs if
  `OPENASSETIO_ENABLE_PYTHON_TEST_VENV` is enabled.
  [#629](https://github.com/OpenAssetIO/OpenAssetIO/issues/629)

- Changed `--install-folder` location of conan install in bootstrap
  scripts from `$CONAN_USER_HOME` to `$WORKSPACE/.conan`. Users who
  have been using the bootstrap scripts directly may need to update
  their toolchain CMake arguments.

### New Features

- Added `simpleResolver.py` example host (under `resources/examples`),
  that provides a basic CLI to resolve Entity References for a supplied
  Trait Set.

- Added CMake option `OPENASSETIO_ENABLE_PYTHON_TEST_VENV`, allowing the
  user to configure whether a python virtual environment is
  automatically created during `ctest` execution, along with a new CMake
  preset `test-custom-python-env` that disables this option.

### Improvements

- Added Python sources to the CMake install tree (rather than requiring
  a separate `pip install` for the pure Python component), effectively
  creating a complete bundle that can be used directly or packaged.
  [#629](https://github.com/OpenAssetIO/OpenAssetIO/issues/629)

- Updated `setup.py` to build the Python extension module. Assuming
  CMake's `find_package` can locate dependencies, then `pip install .`
  is all that is needed to build and install OpenAssetIO into a Python
  environment.
  [#630](https://github.com/OpenAssetIO/OpenAssetIO/issues/630)

- Added 'unstable' warning to docs to notify of python api
  that has not yet been updated for the C++ api,
  and is thus inherently unstable.
  [#600](https://github.com/OpenAssetIO/OpenAssetIO/issues/600)

- Changed CMake configuration so that `openassetio-python-venv` target
  now automatically installs python dependencies of enabled components.
  [#629](https://github.com/OpenAssetIO/OpenAssetIO/issues/629)

- Added convenience methods `debugApi`, `debug`, `info`, `progress`,
  `warning`, `error`, `critical` to `LoggerInterface` to log messages of
  the respective severity.

- Added `OPENASSETIO_CONAN_SKIP_CPYTHON` environment variable to prevent
  conan installing its own python version. This is to support workflows
  where the user is bringing their own python environment, and does not
  want python installations to conflict.
  [#653](https://github.com/OpenAssetIO/OpenAssetIO/issues/653)

- Bleeding edge python wheels are now downloadable as artifacts from the
  `Build wheels` github actions workflow.
  [#653](https://github.com/OpenAssetIO/OpenAssetIO/issues/653)

v1.0.0-alpha.4
--------------

### Breaking changes

- Added checks to the `test.manager.apiComplianceSuite` to ensure
  the correct handling of malformed references.

- Reordered `BatchElementError.ErrorCode` constants to allow grouping of
  entity-related errors.
  [#587](https://github.com/OpenAssetIO/OpenAssetIO/issues/587)

- Migrated `Manager.preflight` and `Manager.register` to use the new
  callback based batch API.
  [#587](https://github.com/OpenAssetIO/OpenAssetIO/issues/587)

- Renamed `apiComplianceSuite` fixtures to disambiguate their use:
  - `a_malformed_reference` -> `an_invalid_reference`
  - `a_malformed_entity_reference` -> `a_malformed_refrence`
  [#585](https://github.com/OpenAssetIO/OpenAssetIO/issues/585)

- Renamed `ResolveErrorCallback` to `BatchElementErrorCallback` for use
  more widely in callback based API functions.
  [#588](https://github.com/OpenAssetIO/OpenAssetIO/issues/588)


### New Features

- Added basic publishing support to the `BasicAssetLibrary` (BAL)
  example manager plugin. This allows rudimentary entity creation
  workflows to be explored. Initially, support is limited to the simple
  in-memory creation/update of entities, with verbatim store/recall of
  the supplied traits data.
  [#585](https://github.com/OpenAssetIO/OpenAssetIO/issues/585)

- Added the `$OPENASSETIO_DEFAULT_CONFIG` mechanism, that allows the
  API to be bootstrapped from a simple TOML file referenced by this
  env var. Presently, this is exposed via the
  `ManagerFactory.createDefaultManagerForInterface` method, which reads
  the manager identifier/settings from this file and returns a suitably
  configured instance of that manager.
  [#494](https://github.com/OpenAssetIO/OpenAssetIO/issues/494)


### Improvements

- Added new `BatchElementError.ErrorCode` constants:
  - `kMalformedEntityReference` When an entity reference is valid, but
    malformed for the calling context and target entity.
  - `kEntityAccessError` When the supplied context's access is the
    specific cause of the error.
  [#587](https://github.com/OpenAssetIO/OpenAssetIO/issues/587)

- Added (protected) `ManagerInterface.createEntityReference` method
  to facilitate the creation of `EntityReference` values as required by
  a manager's implementation.
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)

- Added `TraitsData.traitPropertyKeys` to return a set of the property
  keys for a given trait.
  [#498](https://github.com/OpenAssetIO/OpenAssetIO/issues/498)

- Migrated the `preflight` and `register` `ManagerInterface` methods to
  C++.
  [#588](https://github.com/OpenAssetIO/OpenAssetIO/issues/588)

- Migrated the `preflight` and `register` `Manager` methods to C++.
  [#588](https://github.com/OpenAssetIO/OpenAssetIO/issues/588)

- Reformatted the Python codebase using [black](https://black.readthedocs.io/en/stable/),
  and added CI checks to enforce Python formatting going forward.

### Bug fixes

- Fixed `Manager.resolve` success callback such that the trait data
  provided is compatible with C++ trait views.
  [#605](https://github.com/OpenAssetIO/OpenAssetIO/pull/605)

- Fixed the `RetainPyArgs` Python binding helper to
  work with functions that take `shared_ptr`s by const reference, as
  well as by value. This affected the Python bindings of
  `createManagerForInterface`, which would allow the Python objects given
  to it to go out of scope and be destroyed, despite the associated C++
  objects remaining alive.
  [#620](https://github.com/OpenAssetIO/OpenAssetIO/pull/620)


v1.0.0-alpha.3
--------------

### Improvements

- Added boolean comparison based on content to `EntityReference` types.


### Bug fixes

- Fixed calling `Manager.resolve` from C++, when the manager
  implementation is written in Python.
  [#582](https://github.com/OpenAssetIO/OpenAssetIO/issues/582)


v1.0.0-alpha.2
--------------

### Breaking changes

- Scoped `Context` constants for `access` and `retention` values under
  `Context.Access` and `Context.Retention`, respectively, rather than
  polluting the `Context` namespace with two distinct sets of unrelated
  constants. This uses the more modern `enum class` scoped enumeration
  type in C++.
  [#568](https://github.com/OpenAssetIO/OpenAssetIO/issues/568)

- Scoped `LoggerInterface` severity constants under
  `LoggerInterface.Severity`, for consistency with enumerated constants,
  e.g. `Context` and `BatchElementError`, where enums have their own
  child scope. This uses the more modern `enum class` scoped enumeration
  type in C++.
  [#568](https://github.com/OpenAssetIO/OpenAssetIO/issues/568)

- Changed `resolve` to use a callback-based API, rather than returning
  a list of results.
  [#530](https://github.com/OpenAssetIO/OpenAssetIO/issues/530)

- Removed the `Manager`/`ManagerInterface` `prefetch` method, which
  is redundant now the API is batch-first.
  [#511](https://github.com/OpenAssetIO/OpenAssetIO/issues/511)

- Added `EntityReference` type to encapsulate a validated string
  so it can be used with entity-related API methods. These should always
  be created with either `Manager.createEntityReference` or
  `Manager.createEntityReferenceIfValid`. Updated the signature of
  `Manager` and `ManagerInterface` methods to take `EntityReference`
  object arguments, rather than entity reference strings.
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)

- Renamed `isEntityReference` to `isEntityReferenceString` to avoid
  ambiguity when also working with the new `EntityReference` type.
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)

- Made `isEntityReferenceString` a non-batch method to simplify common
  usage, as it is always in-process.
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)

- Reversed the order of logging severity constants, such that the
  numerical value of the constant increases with the logical severity
  (i.e. `kDebugApi` is now `0` and `kCritical` is now `6`).
  [#516](https://github.com/OpenAssetIO/OpenAssetIO/issues/516)

- Removed the logging abstraction in `HostSession`. The `log` method has
  been replaced with the `logger` accessor that provides the sessions
  `LoggerInterface` derived class directly.
  [#531](https://github.com/OpenAssetIO/OpenAssetIO/issues/531)

- Swapped the order of `severity` and `message` in the
  `LoggerInterface::log` method.
  [#531](https://github.com/OpenAssetIO/OpenAssetIO/issues/531)

- Removed the `Session` Python class in favour of the `ManagerFactory`
  C++/Python class.
  [#430](https://github.com/OpenAssetIO/OpenAssetIO/issues/430)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)
  [#507](https://github.com/OpenAssetIO/OpenAssetIO/issues/507)
  [#510](https://github.com/OpenAssetIO/OpenAssetIO/issues/510)

- Removed redundant `ManagerIntefaceFactoryInterface` methods
  `managers` and `managerRegistered`, whose functionality has been
  migrated to `ManagerFactory`. Removed `instantiateUIDelegate`
  until UI layer work is underway.
  [#505](https://github.com/OpenAssetIO/OpenAssetIO/issues/505)

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
  `PluginSystemManagerFactory` to `ManagerImplementationFactoryInterface`
  and `PythonPluginSystemManagerImplementationFactory`, respectively, to
  avoid potential ambiguity. I.e. that they instantiate (Python)
  instances of `ManagerInterface` rather than `Manager`. For
  consistency and clarity, also prefixed other Python plugin system
  classes with `PythonPluginSystem`.
  [#506](https://github.com/OpenAssetIO/OpenAssetIO/issues/506)
  [#508](https://github.com/OpenAssetIO/OpenAssetIO/issues/508)

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

- Removed the Transactions API, including the `ManagerInterface`
  methods, and `TransactionCoordinator` helpers.
  [#421](https://github.com/OpenAssetIO/OpenAssetIO/issues/421)

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

- Amended the behaviour of `ManagerInterface` such that derived classes
  who implement the `createState` method _must_ also implement
  `createChildState`, `persistenceTokenForState` and
  `stateFromPersistenceToken`. Checks have been added to the
  `openassetio.test.manager` `apiComplianceSuite` to validate manager
  implementations against this requirement.

- Made the constructors of the following classes private: `Context`,
  `Host`, `HostSession`, `Manager`, `TraitsData`. The static `make`
  methods should be used to construct new instances.
  [#481](https://github.com/OpenAssetIO/OpenAssetIO/issues/481)

- Removed the `makeShared` pointer factory. The per-class static `make`
  methods should be used instead.
  [#481](https://github.com/OpenAssetIO/OpenAssetIO/issues/481)


### Features

- Added `openassetio-codegen` tool to auto-generate `Trait` and
  `Specification` classes from simple YAML descriptions.
  [#415](https://github.com/OpenAssetIO/OpenAssetIO/issues/415)


### Improvements

- Added `kEntityResolutionError` and `kInvalidEntityReference` batch
  element error codes, to mirror the `EntityResolutionError` and
  `InvalidEntityReference` exception classes, respectively.
  [#530](https://github.com/OpenAssetIO/OpenAssetIO/issues/530)

- Added `openassetio-python` C++-to-Python bridge library, providing
  a `createPythonPluginSystemManagerImplementationFactory` function,
  which allows a C++ host to load managers using the Python plugin
  system.
  [#508](https://github.com/OpenAssetIO/OpenAssetIO/issues/508)

- Made `LogggerInterface::log` non-const.

- Added `MangerFactory` as a new, simpler, mechanism for querying for
  and instantiating available managers, intended to replace `Session`.
  [#507](https://github.com/OpenAssetIO/OpenAssetIO/issues/507)

- Added `ManagerInterfaceState` abstract base class, that should be
  used as a base for all instances returned from
  `ManagerInterface::createState()`.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)

- Added short-form macros for C API symbols, so that, for example,
  `oa_symbolName` can be used instead of wrapping every reference in the
  namespacing macro, i.e. `OPENASSETIO_NS(symbolName)`.
  [#370](https://github.com/OpenAssetIO/OpenAssetIO/issues/370)

- Migrated the following classes to C++: `Context`, `Host`,
  `HostInterface`, `HostSession` and `LoggerInterface`, `ConsoleLogger`
  `SeverityFilter` and `ManagerImplementationFactoryInterface`. Debug
  and audit functionality is left for future work.
  [#291](https://github.com/OpenAssetIO/OpenAssetIO/issues/291)
  [#331](https://github.com/OpenAssetIO/OpenAssetIO/issues/331)
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#504](https://github.com/OpenAssetIO/OpenAssetIO/issues/504)
  [#507](https://github.com/OpenAssetIO/OpenAssetIO/issues/507)

- Migrated the following `ManagerInterface` methods to C++
  `initialize`, `managementPolicy`, `createState`, `createChildState`,
  `persistenceTokenForState`, `stateFromPersistenceToken`,
  `isEntityReferenceString`, `resolve`.
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)
  [#530](https://github.com/OpenAssetIO/OpenAssetIO/issues/530)

- Migrated the following `Manager` methods to C++ `initialize`
  `managementPolicy`, `createContext`, `createChildContext`,
  `persistenceTokenForContext`, `contextFromPersistenceToken`,
  `isEntityReferenceString`, `resolve`.
  [#455](https://github.com/OpenAssetIO/OpenAssetIO/issues/455)
  [#458](https://github.com/OpenAssetIO/OpenAssetIO/issues/458)
  [#445](https://github.com/OpenAssetIO/OpenAssetIO/issues/445)
  [#549](https://github.com/OpenAssetIO/OpenAssetIO/issues/549)
  [#530](https://github.com/OpenAssetIO/OpenAssetIO/issues/530)

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
