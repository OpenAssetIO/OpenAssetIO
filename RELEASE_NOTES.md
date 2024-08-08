Release Notes
=============

v1.0.0-beta.x.x
---------------

_This release breaks binary compatibility and may break source
compatibility with C++ hosts and managers. In addition, this release may
break source compatibility for Python hosts. See breaking changes
section for more details._

### Breaking changes

- Removed official support for Python 3.7. The minimum supported Python
  version is now Python 3.9.
  [#1365](https://github.com/OpenAssetIO/OpenAssetIO/pull/1365)

- Removed deprecated type aliases `openassetio.TraitsData`,
  `openassetio.BatchElementError`
  and `openassetio.BatchElementException`.
  Removed the deprecated explicit `*BatchElementException` exception
  subtypes under the top-level `openassetio` namespace. Removed the
  deprecated Python `openassetio.exceptions` module. Removed the
  deprecated `kField_*` constants.
  [#1311](https://github.com/OpenAssetIO/OpenAssetIO/issues/1311)

- Marked as "final" several C++ Python bindings of classes that do not
  support Python inheritance, such that an error will be encountered at
  import time if an attempt is made to inherit from them.
  [#1357](https://github.com/OpenAssetIO/OpenAssetIO/pull/1357)

- Updated the API contract to no longer require that managers throw an
  exception when an unrecognized setting is given during initialization.
  The `openassetio.test.manager` API Compliance test suite no longer
  asserts that this is the case.
  [#1202](https://github.com/OpenAssetIO/OpenAssetIO/issues/1202)

- Switched from `std::unordered_set` to `std::set` for trait sets (via
  `TraitSet` alias) in C++. This allows C++ `std` algorithm set
  operations to work. Python is unaffected. This is mostly a
  source-compatible change, provided the `TraitSet` alias is used in
  consuming code, and no `unordered_set`-specific API is used (e.g.
  `reserve(...)`).
  [#1339](https://github.com/OpenAssetIO/OpenAssetIO/issues/1339)

- Source values for `BatchElementError` error codes changed to an
  internally-namespaced `enum` rather than global macros.
  [#1060](https://github.com/OpenAssetIO/OpenAssetIO/issues/1060)

- Removed `OPENASSETIO_GLIBCXX_USE_CXX11_ABI` CMake build option. Builds
  will use the system default libstdc++ ABI, rather than defaulting to
  the old ABI.
  [#1353](https://github.com/OpenAssetIO/OpenAssetIO/issues/1353)

### New Features

- Added SimpleCppManager - a minimal C++ manager and plugin example
  implementation, useful for testing C++ plugin support in hosts. This
  has minimal API support, so [Basic Asset Library (BAL)](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL)
  should still be preferred as a test manager when Python is available.
  [#1324](https://github.com/OpenAssetIO/OpenAssetIO/issues/1324)

- For Windows users, added `OPENASSETIO_DLL_PATH` environment variable
  to allow non-standard Python installations to locate
  `openassetio.dll`, if required.
  [#1340](https://github.com/OpenAssetIO/OpenAssetIO/issues/1340)

- Added `kAuthError` to the set of possible `BatchElementError` error
  codes.
  [#1009](https://github.com/OpenAssetIO/OpenAssetIO/issues/1009)

### Improvements

- Added singular overload of `managementPolicy` for convenience.
  [#856](https://github.com/OpenAssetIO/OpenAssetIO/issues/856)

- Updated the `simpleResolver` example host to support C++ plugins.
  [#1324](https://github.com/OpenAssetIO/OpenAssetIO/issues/1324)

- Added a type hint for the `Manager` instance injected into the
  `openassetio.test.manager` API Compliance test harness, to aid in
  IDE code completion when writing test cases for manager plugins.

### Bug fixes

- Modified OpenAssetIO Python distributions (e.g. installed with `pip
  install`) to allow C++ plugins to load. OpenAssetIO is now bundled as
  multiple shared libraries, allowing external libraries to link.
  [#1340](https://github.com/OpenAssetIO/OpenAssetIO/issues/1340)

- Fixed the (Python-only) `terminology.Mapper` class such that its
  terminology dict can be updated by the manager.
  [#1356](https://github.com/OpenAssetIO/OpenAssetIO/pull/1356)

v1.0.0-beta.2.2
---------------

_This release introduces new features, and remains source compatible._

_The addition of a new virtual method,
 `LoggerInterface.isSeverityLogged`, makes this release a binary incompatibility._

### New Features

- Many types are now printable, with `<<` operators available in C++, and `str`
  and `repr` functions available in python.
  Notably, this includes `TraitsData`, which when printed now displays all the
  properties contained within the traits, rather than simply a list of trait
  ids.

  Note: Due to this, some runtime string output may have slightly changed, and
  tests may need to be adjusted.
  [#1307](https://github.com/OpenAssetIO/OpenAssetIO/issues/1307)

- Added a C++ plugin system. In particular, hosts can use the
  `CppPluginSystemManagerImplementationFactory` class (as a drop-in
  replacement for `PythonPluginSystemManagerImplementationFactory`) in
  order to load C++ manager plugins. Manager plugin authors provide
  a shared library that exposes an `openassetioPlugin` function that
  returns a `PluginFactory` function pointer, which in turn returns
  a `CppPluginSystemManagerPlugin` object.
  [#1115](https://github.com/OpenAssetIO/OpenAssetIO/issues/1115)

- `openassetio.test.manager`, notably used for Api Compliance tests,
  updated to automatically load C++ plugins if a python plugin of the
  requested identifier cannot be found.
  [#1294](https://github.com/OpenAssetIO/OpenAssetIO/issues/1294)

- Added `LoggerInterface.isSeverityLogged` to allow users to
  short-circuit log message construction if the logger indicates the
  intended severity will be filtered. Updated `SeverityFilter` to use
  the most pessimistic of its own severity and that of the wrapped
  logger.
  [#1014](https://github.com/OpenAssetIO/OpenAssetIO/issues/1014)

- Added `utils.substitute` providing a common string substitution format
  using named placeholders in libfmt/Python format string style syntax.
  [#1213](https://github.com/OpenAssetIO/OpenAssetIO/issues/1213)

### Improvements

- Added `getRelationship(s)` and `entityExists` overloads for
  convenience, providing alternatives to the core callback-based
  workflow. Includes more direct methods for singular queries, as
  well as exception vs. result object workflows.
  [#973](https://github.com/OpenAssetIO/OpenAssetIO/issues/973)
  [#1169](https://github.com/OpenAssetIO/OpenAssetIO/issues/1169)

- Added `.pyi` stub files to the Python package to aid IDE code
  completion for Python bindings of C++ types.
  [#1252](https://github.com/OpenAssetIO/OpenAssetIO/issues/1252)

### Deprecated

- Deprecated top level `plugin` variable for python plugins in favour of
  `openassetioPlugin`, in order to reduce risk of conflict with other
  plugin systems, and maintain consistency with the C++ plugin system.
  [#1290](https://github.com/OpenAssetIO/OpenAssetIO/issues/1290)

v1.0.0-beta.2.1
---------------

### Improvements

- Updated `FileUrlPathConverter.pathFromUrl` to automatically convert
  long Windows paths, which exceed the Windows `MAX_PATH` limit, to UNC
  non-normalised device paths (i.e. `\\?\`-prefixed).
  [#1257](https://github.com/OpenAssetIO/OpenAssetIO/issues/1257)

- Added `entityTraits` overloads for convenience, providing alternatives
  to the core callback-based workflow. Includes a more direct method for
  resolving a single entity reference, and exception vs. result object
  workflows.
  [#1217](https://github.com/OpenAssetIO/OpenAssetIO/issues/1217)

v1.0.0-beta.2.0
---------------

### Breaking changes

- Added new required core API method
  `Manager`/`ManagerInterface.entityTraits`, which can be used to
  determine the traits that an existing entity has, or that a new entity
  must have, for a given entity reference.
  [#31](https://github.com/OpenAssetIO/OpenAssetIO/issues/31)

- Renamed access policy for resolving future entities,
  `ResolveAccess.kWrite` to `ResolveAccess.kManagerDriven`. This is then
  consistent with the newly added `managementPolicy` access mode.
  [#1209](https://github.com/OpenAssetIO/OpenAssetIO/issues/1209)

- Access policy keyword argument names in the Python bindings for
  `ManagerInterface` has changed  to `"resolveAccess"` for `resolve` and
  `"policyAccess"` for `managementPolicy`, in order to conform to the
  corresponding C++ argument names.

### New Features

- Added convenience `utils.FileUrlPathConverter` utility class for
  converting `file://` URLs to and from paths. Both POSIX and Windows
  paths (including UNC) are supported in a platform-agnostic way (i.e.
  Windows paths can be processed on POSIX hosts and vice versa).
  [#1117](https://github.com/OpenAssetIO/OpenAssetIO/issues/1117)

- Propagate `OpenAssetIOException`-derived Python exceptions as a
  corresponding C++ exception if a Python method implementation raises
  when transparently called from C++.
  [#947](https://github.com/OpenAssetIO/OpenAssetIO/issues/947)

- Add version accessor methods to allow runtime introspection of
  OpenAssetIO library version. `version.h` header distributed with
  install to allow compile time introspection.
  [#1173](https://github.com/OpenAssetIO/OpenAssetIO/issues/1173)

- Add `managementPolicy` support for querying traits whose required
  properties must be set in order for a publish to succeed, via a
  `kRequired` access mode; and support for querying traits whose
  properties the manager wishes to dictate when publishing, via a
  `kManagerDriven` access mode.
  [#1209](https://github.com/OpenAssetIO/OpenAssetIO/issues/1209)

### Improvements

- Added the string representation of an `EntityReference` when `repr`'d
  in Python.
  [#1186](https://github.com/OpenAssetIO/OpenAssetIO/issues/1186)

- Added basic string representation of a `TraitsData` when `repr`'d
  in Python.
  [#1209](https://github.com/OpenAssetIO/OpenAssetIO/issues/1209)

### Bug fixes

- Throw an exception when attempting to copy-construct a null
  `TraitsData`.
  [#1153](https://github.com/OpenAssetIO/OpenAssetIO/issues/1153)

- Modified no-argument constructor of `Context` to create an empty (but
  non-null) `locale`.
  [#1153](https://github.com/OpenAssetIO/OpenAssetIO/issues/1153)

v1.0.0-beta.1.0
---------------

### Deprecated

> **Note**
> The following deprecated code paths are still available in this
> release, but will be removed in a future version.

- Moved `TraitsData` into the `trait` namespace along with its peer
  container/type definitions.
  [#1127](https://github.com/OpenAssetIO/OpenAssetIO/issues/1127)

- Removed python `exceptions` module in favour of new `errors` module.
  [#1071](https://github.com/OpenAssetIO/OpenAssetIO/issues/1071)

- Moved `BatchElementError` and `BatchElementException` into the
  `errors` namespace.
  [#1071](https://github.com/OpenAssetIO/OpenAssetIO/issues/1071)
  [#1073](https://github.com/OpenAssetIO/OpenAssetIO/issues/1073)

- Removed all subtypes of `BatchElementException`, in favour of a single
  exception type for batch errors raised by the exception throwing
  convenience overloads.
  [#1073](https://github.com/OpenAssetIO/OpenAssetIO/issues/1073)

### Breaking changes

- Updated `ManagerInterface` to reflect which methods are required and
  which are optional, default method implementations have been updated:

  - Pre-initialization methods are a no-op or return empty data.
  - Post-initialization methods raise a `NotImplementedException`.

  Note that in order to support multi-language plugins, pure virtual/ABC
  is not used to denote required methods in all cases. See the class API
  documentation for more details.
  [#163](https://github.com/OpenAssetIO/OpenAssetIO/issues/163)

- Added the (required) `Manager`/`ManagerInterface` `hasCapability`
  method. A mechanism to query which particular capabilities a manager
  implements. This allows a Host to avoid `NotImplementedException`s
  when a specific capability has not been implemented by any given
  manager.
  [#DR022](doc/decisions/DR022-Default-method-implementations.md),
  [#1113](https://github.com/OpenAssetIO/OpenAssetIO/issues/1113)

- Removed non-paged versions of the `Manager`/`ManagerInterface`
  relationship query methods and renamed the paged methods to remove
  the `Paged` suffix. `PagedRelationshipSuccessCallback` has been
  renamed to `RelationshipQuerySuccessCallback` to better reflect the
  default of pagination, and reduce ambiguity when relationship creation
  methods are added in the future.
  [#1125](https://github.com/OpenAssetIO/OpenAssetIO/issues/1125)

- Attempting to retrieve a trait property with
  `TraitsData.getTraitProperty` or using trait view classes no longer
  raises an exception if the trait itself is missing. This simplifies
  many common access patterns, and can remove the need for
  `hasTrait`/`isImbuedTo` checks.
  [#970](https://github.com/OpenAssetIO/OpenAssetIO/issues/970)

- Added [fmt](https://fmt.dev/9.1.0) as a new header-only private
  dependency.
  [#1070](https://github.com/OpenAssetIO/OpenAssetIO/issues/1070)

- Removed `const` from the majority of interface methods to allow
  implementations to make use of private state for efficiency reasons.
  [#518](https://github.com/OpenAssetIO/OpenAssetIO/issues/518)

- `errors.h` renamed to `errors/errorCodes.h`
  [#1073](https://github.com/OpenAssetIO/OpenAssetIO/issues/1071)

- Removed the "Sample Asset Manager" example, which was wholly out of
  date, and has been superseded by the [standalone manager template
  repository](https://github.com/OpenAssetIO/Template-OpenAssetIO-Manager-Python).

- Changed success/return type of `defaultEntityReference` to wrap in
  `std::optional`. Updated expected manager response such that an
  optional without a value signals that no default is available for an
  otherwise valid query. Changed default implementation to respond with
  an empty optional in the success callback, rather than error.
  [#1100](https://github.com/OpenAssetIO/OpenAssetIO/issues/1100)

- The middleware will validate that the manager's implementation provides
  the `kEntityReferenceIdentification` and `kManagementPolicyQuery`
  capabilities upon initialization.
  [#1148](https://github.com/OpenAssetIO/OpenAssetIO/issues/1148)

### New Features

- Added new exception types, allowing all OpenAssetIO exceptions to
  share a common base.
  [#1071](https://github.com/OpenAssetIO/OpenAssetIO/issues/1071)

- Exceptional conveniences now provide additional information such
  as entityReference, index, access, and error type in the message
  of the exception.
  [#1073](https://github.com/OpenAssetIO/OpenAssetIO/issues/1073)

### Improvements

- Modified Python bindings for all non-trivial methods such that they
  release the GIL before calling any underlying C++ implementation.
  [#554](https://github.com/OpenAssetIO/OpenAssetIO/issues/554)

- Improved error messaging when `defaultManagerForInterface` points to a
  directory not a file.

- Added some protection for accidental overwrites of a CMake installed
  `openassetio` Python package, by installing a `.dist-info` metadata
  directory alongside the package. `pip install` will then fail/warn
  against accidental overwrites/overrides. Added a CMake
  variable `OPENASSETIO_ENABLE_PYTHON_INSTALL_DIST_INFO` to disable this
  feature.
  [#1088](https://github.com/OpenAssetIO/OpenAssetIO/issues/1088)

- `Manager.createContext` does not call `ManagerInterface.createState`
  if manager is not capable of `kStatefulContexts`, in which case the
  `Context` is returned without a `managerState`.
  [#163](https://github.com/OpenAssetIO/OpenAssetIO/issues/163)

- Removed the unused `PythonPluginSystemManagerPlugin.uiDelegate`
  method, along with associated UI related documentation that referenced
  non-existent functionality.
  [#1150](https://github.com/OpenAssetIO/OpenAssetIO/issues/1150)

- Clarified `ManagerInterface` documentation around the relative
  "stateless" nature of the API and its reentrant design.
  [#1143](https://github.com/OpenAssetIO/OpenAssetIO/issues/1143)

v1.0.0-alpha.14
---------------

### Breaking changes

> **Warning**
>
> - Removed `Context.Access` and instead added per-workflow access mode
>  enumerations under an `access` namespace. Added these enums as
>  required arguments to various API functions, replacing the usage of
>  `Context.Access`.
>  [#1054](https://github.com/OpenAssetIO/OpenAssetIO/issues/1054)
>
> - Changed signature of `preflight` to accept a `TraitsData` per
>   reference, rather than a single trait set. The host is now expected to
>   communicate any relevant information that it owns and is known at
>   `preflight` time.
>   [#1028](https://github.com/OpenAssetIO/OpenAssetIO/issues/1028)

- Relaxed the restriction on `register` that all trait sets of the
  provided `TraitsData` elements must match. This allows batched
  publishing of heterogeneous entity types.
  [#1029](https://github.com/OpenAssetIO/OpenAssetIO/issues/1029)

- Removed `cpython` dependency from `conanfile.py`. When building
  OpenAssetIO, it is now expected that a development install of the
  appropriate Python version is discoverable on the system.
  [#1038](https://github.com/OpenAssetIO/OpenAssetIO/pull/1038)

- Migrated manager methods `entityExists` and `defaultEntityReference`
  to C++ with Python bindings, and redesigned to use a callback based
  batch API.
  [#992](https://github.com/OpenAssetIO/OpenAssetIO/issues/992)
  [#993](https://github.com/OpenAssetIO/OpenAssetIO/issues/993)

- Migrated `ManagerInterface`/`Manager` `updateTerminology` to C++ with
  Python bindings. Tweaked interface to be returned based rather than
  out-param based.
  [#996](https://github.com/OpenAssetIO/OpenAssetIO/issues/996)

- Removed `kWriteMultiple` and `kReadMultiple` access patterns, due to
  not having coherent use cases.
  [#1016](https://github.com/OpenAssetIO/OpenAssetIO/issues/1016)

- Removed `Context.Retention` due to not having coherent use cases.
  [#1048](https://github.com/OpenAssetIO/OpenAssetIO/issues/1048)

### New Features

- Added `kCreateRelated` access pattern, to indicate when a workflow
  specifically creates a new entity as a relation to an existing one.
  [#1016](https://github.com/OpenAssetIO/OpenAssetIO/issues/1016)

- Added `BatchElementError.ErrorCode.kInvalidTraitSet` and
  `InvalidTraitSetBatchElementException`.
  [#992](https://github.com/OpenAssetIO/OpenAssetIO/issues/992)

### Improvements

- Increased verbosity when running the `openassetio.test.manager` API
  compliance suite test harness. The report includes tests that were
  skipped, helping to detect accidentally omitted fixtures.
  [1032](https://github.com/OpenAssetIO/OpenAssetIO/pull/1032)

- Added some aliases to the Doxygen API documentation. In
  particular, `Ptr` and `ConstPtr` aliases are now cross-referencable.

- Altered the fixture that causes a skip in relationship based API
  compliance tests, to be the more specific relationship traitset.
  [#1022](https://github.com/OpenAssetIO/OpenAssetIO/issues/1022)

- Set the correct context for various tests in the API Compliance
  `openassetio.manager.test` test harness.

v1.0.0-alpha.13
---------------

### Breaking changes

- Refactored `getRelatedReferences` into `getWithRelationship` and
  `getWithRelationships` to better define the two possible batch-axis,
  and simplify implementation on both sides of the API. This also
  changes the methods over to callback signatures for consistency with
  the rest of the API, and migrates them to C++ with Python bindings.
  [#847](https://github.com/OpenAssetIO/OpenAssetIO/issues/847)
  [#919](https://github.com/OpenAssetIO/OpenAssetIO/issues/919)
  [#913](https://github.com/OpenAssetIO/OpenAssetIO/issues/913)

- Removed version query APIs (`entityVersion`, `entityVersions`,
  `finalizedEntityVersion`) in favour of use of the more general
  `resolve` and `getWithRelationship` methods. See
  [DR017](./doc/decisions/DR017-Entity-version-queries.md) for
  details.
  [#980](https://github.com/OpenAssetIO/OpenAssetIO/issues/980)

- Updated `castToPyObject` to convert a `nullptr` input to a Python
  `None`, rather than throwing an exception.
  [#988](https://github.com/OpenAssetIO/OpenAssetIO/issues/988)

- Removed out of date constants from the Python `openassetio.constants`
  module. These have been replaced by domain-specific traits and
  specifications defined in their own repositories, such as
  [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation).

- Migrated remaining constants to C++ with Python bindings. This means
  that `from openassetio.constants import <name>` no longer works - the
  `constants` module must be imported wholesale.
  [#998](https://github.com/OpenAssetIO/OpenAssetIO/issues/998)

### Deprecated

- Renamed manager info dictionary key constants, which were prefixed
  with `kField_`, to use an `InfoKey_` prefix instead. The deprecated
  constant variables will be removed in a future release.
  [#998](https://github.com/OpenAssetIO/OpenAssetIO/issues/998)

### Improvements

- Added paged implementations of `getWithRelationship` and
  `getWithRelationships`, called `getWithRelationshipPaged` and
  `getWithRelationshipsPaged`. These methods are the equivalent of the
  non-paged versions, but provide an `EntityReferencePager` object,
  rather than a direct list of results, allowing for correct handling of
  extremely large/unbounded data sets.
  [#971](https://github.com/OpenAssetIO/OpenAssetIO/issues/971)

- Added default implementations of `getWithRelationship` and
  `getWithRelationships` that return empty lists, making these methods
  opt-in for manager implementations.
  [#163](https://github.com/OpenAssetIO/OpenAssetIO/issues/163)

- Added coverage of the `getWithRelationship[s]` and
  `getWithRelationship[s]Paged` methods of the `ManagerInterface` to the
  `openassetio.manager.test` harness.
  [#914](https://github.com/OpenAssetIO/OpenAssetIO/issues/914)
  [#972](https://github.com/OpenAssetIO/OpenAssetIO/issues/972)

- Added `requireEntityReferenceFixture` and
  `requireEntityReferencesFixture` utility methods for cases written for
  the `openassetio.test.manager` (aka `apiComplianceSuite`) test
  harness. These convert a string fixture into an `EntityReference`
  object, or a list-of-strings fixture into a list of `EntityReference`
  objects, respectively.
  [#914](https://github.com/OpenAssetIO/OpenAssetIO/issues/914)

- Migrated the `ManagerInterface`/`Manager` `flushCaches` method to C++
  with Python bindings.
  [#994](https://github.com/OpenAssetIO/OpenAssetIO/issues/994)

- Added a call to `flushCaches` after every `openassetio.test.manager`
  (aka `apiComplianceSuite`) test case, giving the manager plugin a
  chance to clean up between tests.
  [#994](https://github.com/OpenAssetIO/OpenAssetIO/issues/994)

### Bug fixes

- Reintroduced the optional optimized entity reference prefix check
  for `isEntityReferenceString`, allowing the plugin's implementation to
  be short-circuited. In particular, if the plugin's implementation is
  written in Python, then a prefix check short-circuits the need for a
  costly Python function call for this hot code path.
  [#566](https://github.com/OpenAssetIO/OpenAssetIO/issues/566)

v1.0.0-alpha.12
---------------

### New Features

- Added an overload of `ManagerFactory.defaultManagerForInterface` that
  takes a config file path string argument, rather than using an
  environment variable.
  [#937](https://github.com/OpenAssetIO/OpenAssetIO/issues/937)

- Added support for `${config_dir}` interpolation within manager string
  settings retrieved from the TOML config file used by
  `defaultManagerForInterface`. This token expands to the absolute
  directory of the TOML config file.
  [#804](https://github.com/OpenAssetIO/OpenAssetIO/issues/804)

v1.0.0-alpha.11
---------------

### Breaking changes

- `Manager.createChildContext` now deep-copies the parent locale to
  prevent subsequent modifications of the locale of one context
  from affecting the other.
  [#896](https://github.com/OpenAssetIO/OpenAssetIO/issues/896)

- Removed `ManagerInterface.setRelatedReferences` pending re-design.
  [#16](https://github.com/OpenAssetIO/OpenAssetIO/issues/16)

- Simplified the locale `TraitsData` provided to API compliance tests
  via the `openassetio.test.manager` test harness. The locale now
  contains only a single `"openassetio:test.locale"` trait with a
  `"case"` property giving the name of the `unittest` test case.
  [#835](https://github.com/OpenAssetIO/OpenAssetIO/issues/835)

- Removed the `TraitBase` and `SpecificationBase` classes. Trait and
  specification view classes are no longer part of the core API and are
  instead auto-generated by the OpenAssetIO-TraitGen tool.
  [#835](https://github.com/OpenAssetIO/OpenAssetIO/issues/835)

- Changed the arguments of `BatchElementErrorCallback` and
  `ResolveSuccessCallback` from reference types to value types.
  [#858](https://github.com/OpenAssetIO/OpenAssetIO/issues/858)

### New Features

- Added utility methods `castToPyObject` and `castFromPyObject` to
  `openassetio-python-bridge` to facilitate converting between C++ and
  Python objects for hosts seeking to support mixed language workflows.
  Note : Some methods on `Manager` and `ManagerInterface` are currently
  implemented in python, pending imminent port to C++. Due to this,
  these methods will not yet be available for use on a python object
  returned from `castToPyObject`.
  [#798](https://github.com/OpenAssetIO/OpenAssetIO/issues/798)

### Improvements

- Added support for running `ctest` when a python venv is used to
  determine which Python distribution to build against.

- `HostSession` methods `logger` and `host` now return a const
  reference to the held pointer rather than a copy.
  [#815](https://github.com/OpenAssetIO/OpenAssetIO/issues/815)
  [#904](https://github.com/OpenAssetIO/OpenAssetIO/issues/904)

- Contexts are now created with an empty `TraitsData` in their locale,
  this makes testing for imbued traits easier as it can be assumed that
  the pointer is never null.
  [#903](https://github.com/OpenAssetIO/OpenAssetIO/issues/903)

- `EntityReference` objects are now coercible to strings in Python,
  allowing more intuitive use with `format`, `print`, and others.
  [#573](https://github.com/OpenAssetIO/OpenAssetIO/issues/573)

- Added `Ptr`/`ConstPtr` alias members to all appropriate C++ classes,
  aliasing the associated `shared_ptr` of that class.
  [#918](https://github.com/OpenAssetIO/OpenAssetIO/issues/918)

- Added support for building for Python 3.11
  [#683](https://github.com/OpenAssetIO/OpenAssetIO/issues/683)

v1.0.0-alpha.10
---------------

### Breaking changes

- Renamed `TraitBase.isValid` to `isImbued` for symmetry with
  `imbue`/`imbueTo` methods.
  [#815](https://github.com/OpenAssetIO/OpenAssetIO/issues/815)

- Changed the host identifier, and removed the custom locale from the
  `simpleResolver` example as they did not follow best practice.

- `BatchElementErrorCallback` moved from the top level `openassetio`
   namespace to the `openassetio::hostApi::Manager` namespace.
   [#849](https://github.com/OpenAssetIO/OpenAssetIO/issues/849)

- Removed the `entityName` and `entityDisplayName` methods in favour of
  resolvable traits to minimize API calls and allow industry specific
  flexibility. See OpenAssetIO-MediaCreation.
  [#837](https://github.com/OpenAssetIO/OpenAssetIO/issues/837)

### New features

- Added `TraitBase.isImbuedTo` static/class method, giving a cheaper
  mechanism for testing whether a `TraitsData` is imbued with a trait.
  [#815](https://github.com/OpenAssetIO/OpenAssetIO/issues/815)

- Added `resolve`, `preflight` and `register` overloads for
  convenience, providing alternatives to the core callback-based
  workflow. Includes a more direct method for resolving a single entity
  reference, and exception vs. result object workflows.
  [#849](https://github.com/OpenAssetIO/OpenAssetIO/issues/849)
  [#850](https://github.com/OpenAssetIO/OpenAssetIO/issues/850)
  [#851](https://github.com/OpenAssetIO/OpenAssetIO/issues/851)
  [#852](https://github.com/OpenAssetIO/OpenAssetIO/issues/852)
  [#853](https://github.com/OpenAssetIO/OpenAssetIO/issues/853)
  [#854](https://github.com/OpenAssetIO/OpenAssetIO/issues/854)

### Improvements

- Improved the documentation for the `simpleResolver` example, to
  provide more context when using it as a starting point for an
  OpenAssetIO integration.

- Update the pybind dependency version to 2.10.1.
  [#863](https://github.com/OpenAssetIO/OpenAssetIO/issues/863)

- Made `BatchElementError` a copyable type in the C++ API.
  [#849](https://github.com/OpenAssetIO/OpenAssetIO/issues/849)

- Added equality/inequality comparison operators to `BatchElementError`.
  [#862](https://github.com/OpenAssetIO/OpenAssetIO/issues/862)

- Made the C++ codebase compliant with Clang-Tidy v15. Note that this is
  not yet enforced on CI.
  [#874](https://github.com/OpenAssetIO/OpenAssetIO/pull/874)

### Bug fixes

- Removed `nodiscard` from `TraitsData::getTraitProperty`, and
  `TraitBase::getTraitProperty`, to allow "value or default" style use
  cases.
  [#825](https://github.com/OpenAssetIO/OpenAssetIO/issues/825)

v1.0.0-alpha.9
--------------

### Breaking changes

- Disabled the (nascent) C bindings by default. To enable, the
  `OPENASSETIO_ENABLE_C` CMake option must be explicitly set to `ON`.

### New features

- The `FixtureAugmentedTestCase` class of the
  `openassetio.test.manager.harness` can now be configured to create a
  new, uninitialized manager instance for each test case, by setting the
  `shareManger` class variable or derived classes to `False`. This
  facilitates testing of a manager's initialization behavior.
  [BAL#26](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL/issues/26)

### Bug fixes

- Ensured that the Python GIL is acquired within
  `createPythonPluginSystemManagerImplementationFactory`, so that it is
  no longer necessary to acquire externally by the calling (host)
  thread.
  [#797](https://github.com/OpenAssetIO/OpenAssetIO/issues/797)

- Fixed use-after-free issue in hybrid C++/Python applications, where
  the Python interpreter is destroyed before OpenAssetIO objects are
  cleaned up. This could manifest as segfaults or hangs at program exit.
  [#805](https://github.com/OpenAssetIO/OpenAssetIO/pull/805)

v1.0.0-alpha.8
--------------

### Breaking changes

- The `openassetio.traits` module has been removed. OpenAssetIO
  itself no longer contains any trait definitions. Integrations of the
  API should use the established standards particular to the area of
  use. See [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation)
  for traits previously included here.
  [#717](https://github.com/OpenAssetIO/OpenAssetIO/issues/717)

v1.0.0-alpha.7
--------------

### Breaking changes

- OpenAssetIO now has a soft dependency on the `importlib_metadata`
  Python package (>=3.6.0). If you have been installing the project
  manually by extending `PYTHONPATH` (instead of using `pip`) you may
  also need to additionally satisfy this dependency if you wish to make
  use of entry point based discovery of Python plugins.
  [#762](https://github.com/OpenAssetIO/OpenAssetIO/issues/762)

- The `PythonPluginSystem` no longer clears existing plugin
  registrations when `scan` is called. The
  `PythonPluginSystemManagerImplementationFactory` has been updated to
  call `reset` itself, so this change only affects any direct use of the
  `PythonPluginSystem` by third party code.
  [#703](https://github.com/OpenAssetIO/OpenAssetIO/issues/703)

- The `PythonPluginSystemManagerImplementationFactory` now checks
  fall-back environment variables during construction, rather than the
  first time plugins are queried. This means changes to the environment
  made after a factory has been created will not affect that factory.
  [#762](https://github.com/OpenAssetIO/OpenAssetIO/issues/762)

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

### New features

- Added entry point based discovery of Python manager plugins. This
  allows pure Python manager plugins to be deployed and managed as
  Python packages, without the need to wrangle
  `OPENASSETIO_PLUGIN_PATH`. The `openassetio.manager_plugin` entry
  point should expose a module providing a top-level `plugin` variable,
  holding a `ManagerPlugin` derived class. This can be disabled by
  setting the `OPENASSETIO_DISABLE_ENTRYPOINTS_PLUGINS` env var to any
  value.
  [#762](https://github.com/OpenAssetIO/OpenAssetIO/issues/762)

### Improvements

- Added `openassetio-build` docker image. This is an extension of the
  already used [ASFW CY22 docker image](https://hub.docker.com/r/aswf/ci-base/tags?name=2022),
  but with the additional OpenAssetIO dependencies installed into it.
  As we have also installed test dependencies into this image, this
  unlocks out-of-the-box sandboxed testing workflows via docker.
  [#716](https://github.com/OpenAssetIO/OpenAssetIO/issues/716)

- Reorganized the directory structure to better reflect the fact that
  the project is split into distinct components, and that it is
  primarily a CMake-driven project with optional Python component.
  [#655](https://github.com/OpenAssetIO/OpenAssetIO/issues/655)

- Improved documentation for users that wish to build/release
  OpenAssetIO.
  [#624](https://github.com/OpenAssetIO/OpenAssetIO/issues/624)
  [#716](https://github.com/OpenAssetIO/OpenAssetIO/issues/716)
  [#749](https://github.com/OpenAssetIO/OpenAssetIO/pull/749)

- Improved support for consumption of OpenAssetIO by downstream CMake
  projects. `OpenAssetIOConfig.cmake` provides variables for locating
  the installation location of binaries and Python sources. When used as
  a CMake subproject, namespaced `ALIAS` targets match the exported
  targets, and the build-tree has `RPATH` support.
  [#675](https://github.com/OpenAssetIO/OpenAssetIO/pull/675)

### Bug fixes

- Fixed various broken URLs in markdown docs.
  [#744](https://github.com/OpenAssetIO/OpenAssetIO/pull/744)

- Fixed unnecessary link dependencies on Python and pybind11 when
  building and linking to the `openassetio-python-bridge` library.
  [#675](https://github.com/OpenAssetIO/OpenAssetIO/pull/675)

- Fixed the file extension for Windows debug builds of the
  `_openassetio` Python extension module.
  [#675](https://github.com/OpenAssetIO/OpenAssetIO/pull/675)

- Fixed `.pdb` debug symbol files installation location on Windows.
  [#675](https://github.com/OpenAssetIO/OpenAssetIO/pull/675)

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
