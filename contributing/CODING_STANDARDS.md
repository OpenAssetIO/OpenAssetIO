# Coding Standards

### Line wrapping

Line wrapping is performed at 99 characters for code, and 72 characters
for docstrings and comments (as per PEP8).

This also applies to C++ code - 99 characters, apart from comments that
we strive to keep within 72 characters.

For markdown documents, line wrapping is also performed at 72
characters, where possible.

### C++

We mostly follow the [Google Style Guide](https://google.github.io/styleguide/cppguide.html)
with a few exceptions, as detailed in the configuration of the linters
described below.

CI is configured to enforce [Clang-Format](https://clang.llvm.org/docs/ClangFormat.html),
[Clang-Tidy 12](https://releases.llvm.org/12.0.0/tools/clang/tools/extra/docs/clang-tidy)
and [Cpplint](https://github.com/cpplint/cpplint) checks.

Clang-Tidy and Cpplint can be enabled as part of the build process using
CMake boolean variables `OPENASSETIO_ENABLE_CLANG_TIDY` and
`OPENASSETIO_ENABLE_CPPLINT`, respectively.

Clang-Format is configured as per the `.clang-format` at the root of the
repository. 

Similarly, Clang-Tidy is configured as per the `.clang-tidy`
at the root of the repository, but with the additional command-line flag
`-extra-arg=-Wno-unknown-warning-option` to avoid false positives when 
using GCC.

Cpplint is configured as per the `CPPLINT.cfg` in the `src` directory,
but with the additional command-line flag 
`--includeorder=standardcfirst` to avoid false positives with 
third-party libraries.

### Python

For Python code we aim to adhere to the PEP8 convention, with a few
exceptions. Of these exceptions, the most obvious is that the naming
scheme is designed to more closely mirror our C++ naming conventions,
to ease C++ interop implementation and readability.

### Example code

An exception to the above is for code examples written in Python. Here,
PEP8 should be strictly followed, including its naming conventions.

### Method/function naming

Accessor (getter) methods that do not have a corresponding mutator
(setter) method at the same or higher access level (e.g. public getter
vs. private setter) _should not_ be prefixed with `get`.

If a getter does have a corresponding setter at the same or higher
access level (e.g. protected getter vs. public setter), then they
_should_ be prefixed with `get` and `set`, respectively.

This makes it easier to determine the API surface at a glance.

### Test cases

Where feasible, Python unit test cases should use a class for each unit,
where the methods of the test class are the test cases for that unit. In
addition, test cases should ideally be written using `when` and `then`
to delineate action/input and postcondition. The name of the test class
itself should begin with `Test_`. For example,

```python
class Test_UnitName:
    def test_when_action_then_postcondition(self, ...):
        ...
```

Often the unit under test is a class method, in which case the test
class name should include the method under test preceded by its class,
separated by an underscore. For example,

```python
class Test_ManagerInterface_entityVersion:
    ...
```

Don't be afraid of long test case names (up to the 99 character line
length limit).

Sometimes the test is trivial, in that the unit is small and only has
one code path. In that case shoehorning a test case description into a
`when`/`then` style may be less readable than a simpler ad-hoc
alternative. Best judgement should be used, bearing in mind readability
and consistency tradeoffs.

### IDE configuration

To aid in conforming to our coding style a [`.editorconfig`](https://editorconfig.org/)
file is included in the root of the repository, which has wide support
across various IDEs. For supported IDEs this config file can override
the default settings for inspections and formatting refactors.

In particular, more granular settings are included for IntelliJ-based
IDEs (for example, PyCharm) via the `ij_*` extensions.

Common file types that we expect to encounter during development of
OpenAssetIO have their own settings, many of which remain commented out
for reference and may be enabled and tweaked in future.

As mentioned in the [C++](#c) section above, a `.clang-format` 
configuration for C++ is included at the root of the repository, which
has wide support in various IDEs to aid in auto-formatting.

### Environment variables

All environment variables should be prefixed with `OPENASSETIO_`.
For example, `OPENASSETIO_LOGGING_SEVERITY`.

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment
Variable List_ page of the generated documentation.

### Parameter documentation

All method parameters should be documented in docstrings or doxygen
comment blocks.

In Python, as our configuration can't determine parameter types, we must
manually specify those. This should be in the following form for
OpenAssetIO defined types:

```
@param <name> <path> "<short.path>" Description text.
```

And the following, for built-ins or external types (note the backticks):

```
@param <name> `<external_type>` Description text.
```
