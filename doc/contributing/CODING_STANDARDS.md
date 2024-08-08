# Coding Standards

This document covers the specifics of how code should be structured.
Details on code formatting conventions can be found in the
[Coding Style](CODING_STYLE.md) guide.

## Method/function naming

Accessor (getter) methods that do not have a corresponding mutator
(setter) method at the same or higher access level (e.g. public getter
vs. private setter) _should not_ be prefixed with `get`.

If a getter does have a corresponding setter at the same or higher
access level (e.g. protected getter vs. public setter), then they
_should_ be prefixed with `get` and `set`, respectively.

This makes it easier to determine the API surface at a glance.

## Test cases

### CTest

Our tests are broadly grouped into CMake [CTest](https://cmake.org/cmake/help/v3.23/manual/ctest.1.html)
targets. This includes Python tests, whose CTest target(s) delegate to
[pytest](https://docs.pytest.org).

There are CTest [fixture tests](https://cmake.org/cmake/help/v3.23/prop_test/FIXTURES_REQUIRED.html),
which run set-up and tear-down steps. In particular, these create a
(Python) environment and install the project into it, so that tests can
be run against the install tree, rather than the build tree.

In order to facilitate parallel test execution, CMake build target
dependencies should be carefully considered. CTest will execute each
test in a separate process, and so will re-resolve any CMake build
target dependencies for every test, potentially reproducing work
unnecessarily, or even causing the build/test to fail due to race
conditions (when executed in parallel). Instead, create a build target
with minimal dependencies, then add the dependencies using CTest fixture
tests. If a build target with non-trivial dependencies is still
required, create a wrapper build target that executes the original, and
configure only the wrapper build target to have the additional
dependencies.

Convenience CMake functions `openassetio_add_test_target`,
`openassetio_add_test_fixture_target` and
`openassetio_add_test_fixture_dependencies` can be used for adding
a CMake target as a CTest test, adding a CMake target as a CTest
fixture, and configuring the dependencies between fixtures and tests
(including other fixtures), respectively.

In particular, the `openassetio_add_test_target` function will add a
`LABEL` property with the value `"Test"`, which is useful for
disambiguating fixtures from tests.

### Python

Python code should be written using only features included in Python
3.10.

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
and consistency trade-offs.

### ABI checks

When the OpenAssetIO C/C++ ABI changes, we need to know about it to
inform our release notes and semver versioning.

We try to avoid breaking changes more than most projects, due to the
nature of software adoption in the VFX industry, where tools can be
pinned to a major/minor release for several years before an upgrade is
allowed.

To help monitor breaking changes we have automated checks against C++
ABI snapshots. See [resources/abi](../../resources/abi/README.md) for
more details.

## C++

### Classes

#### Smart pointers

C++ classes that represent system components with reference semantics
(as opposed to 'value' types) should define both a qualified peer
`ClassNamePtr` alias and an unqualified member `Ptr` alias, using
`std::shared_ptr`. Their constructors should be private, and a static
`make` method provided.

This is to simplify memory management across the complex range of
language bindings within the project.

There is a convenience macro `OPENASSETIO_DECLARE_PTR` available in
`typedefs.hpp` that should be used to declare the `shared_ptr`. A macro
gives us a single point of change should we wish to alter or add more
declarations.

The `OPENASSETIO_ALIAS_PTR` macro should then be used to declare
`shared_ptr` alias members.

Usage example:

```cpp
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(Host)

class OPENASSETIO_CORE_EXPORT Host final {
public:
    OPENASSETIO_ALIAS_PTR(Host)

    static HostPtr make(...);

private:
    Host(...);
}
...
```

#### Forward declarations

To decrease coupling and improve compile times it is idiomatic in C++ to
forward declare classes when the full definition is not yet required, so
that `#include`ing the class's associated header can be deferred until
needed (typically within the `.cpp` source file).

There is a convenience macro `OPENASSETIO_FWD_DECLARE` in `typedefs.hpp`
that should be used to forward declare classes. The macro wraps the
class declaration in the appropriate top-level namespaces, plus
optionally a child namespace (depending on whether one or two arguments
are provided). Hence the macro should be used _outside_ of any other
namespace.

Usage example:

```cpp
#include <openassetio/typedefs.hpp>

OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
...
```

> **Warning**: The Windows MSVC compiler mangles `struct` and `class`
> declarations differently in the compiled binary. Since the above
> macro forward declares using `class`, we must avoid using `struct`
> to define classes or we risk linker errors on Windows.

### Enumerations

All enumerations in C++ should use scoped enumerations, i.e.
`enum class`, to ensure constants do not pollute the parent namespace,
and to add strong typing, avoiding a class of programmer error. This
matches the [ISO C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Renum-class).

Python bindings should therefore not use [export_values()](https://pybind11.readthedocs.io/en/stable/classes.html#enumerations-and-internal-types)
when binding a scoped enum type, for consistency with C++. That is,
when binding a C++ `enum class` using pybind, use
`py::enum_<...>{...}.value(...)` without the common terminating
`.export_values()`. This then ensures the enum is available in Python
namespaced in the same way as in C++, i.e. not polluting the parent
namespace.

### Const

Methods of interface classes, and their corresponding wrapper class
methods should not be marked `const`. For example, `ManagerInterface` +
`Manager`, `HostInterface` and `Host`. This allows the implementation to
maintain private state to service the API requests if neccesary.

## String formatting

The project has a (private, header-only) dependency on the
[fmt](https://fmt.dev/9.1.0) library for efficient string formatting,
and this should be used by preference over alternative legacy options
such as `std::stringstream`.

> **Note**
>
> Due to a [symbol leakage issue](https://github.com/fmtlib/fmt/issues/3626)
> in the current latest fmt version v10.1, we recommend (and build/test
> with) fmt v9.1.

## C

### Handles

C Handles that manage reference semantics objects should always use a
`<T>Ptr` over a raw pointer, and use a `Shared` suffix in their naming,
to facilitate object exchange through multiple languages bindings.

```cpp
using SharedMyClass = Converter<MyClassPtr, oa_SharedMyClass_h>;
```

## Python bindings

### Holder classes for reference-semantic types

When binding something with reference semantics to python, the holder
should always be a `<T>Ptr`. `pybind` understands `std::shared_ptr`, and
this avoids memory management issues when objects are exchanged through
multiple language bindings.

```cpp
py::class_<MyClass, MyClassPtr>(module, "MyClass")
  ...
```

### Methods with pointer arguments

When binding methods that take a `<T>Ptr`, (almost) always use the
`.none(false)` modifier to ensure `None` is not implicitly converted to
a null pointer.

```cpp
    .def("setHost", py::arg("host").none(false))
```

### Polymorphic override macros

In order to support C++ class instances transparently calling into a
mirrored Python instance, pybind11 has support for so-called
["trampoline" classes](https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python),
which dispatch either to the Python method override, or to the C++ base
class implementation if no Python override is found. Method bodies
use convenience macros to implement this logic.

In pybind11, any exception that occurs in Python, and propagates to C++,
is translated to an `error_already_set` C++ exception. In order to
support Python->C++ exception type translation, we must augment the
pybind11 macros.

So instead of using the `PYBIND11_OVERRIDE_*` family of macros, we must
use `OPENASSETIO_PYBIND11_OVERRIDE_*`, which decorates the pybind11
implementation with additional functionality, such as exception
translation.

### Python object lifetime

Due to a [Pybind issue](https://github.com/pybind/pybind11/issues/1333),
it is possible for a Python object to be destroyed even if a C++
instance holds a `shared_ptr` to it (via a pointer to base class
instance).

This causes problems in particular when we use Pybind "trampoline"
classes to call a Python method override from a C++ virtual member
function. For example, if the Python instance is destroyed, then in the
case of pure virtual member functions, `pybind` may throw an exception

```
RuntimeError: Tried to call pure virtual function
```

As a workaround until there is an upstream fix, we have introduced a
`PyRetainingSharedPtr` type, which should be used as the argument type
and return type for any C++ bindings where the Python instance going
into C++ must be kept alive.

#### Constructors

For constructors bound using the `pybind11::init<Args...>()` helper
(where `Args...` is the signature of the constructor), it is sufficient
to replace any `shared_ptr` types (whose associated Python instance must
be kept alive) in `Args` to instead be `PyRetainingSharedPtr` types.

#### Return values

To handle instances returned from a Python method to C++ we must modify
the `PYBIND11_OVERRIDE` macro arguments in the Pybind "trampoline" class
member functions from, for example

```c++
std::shared_ptr<MyReturnType> PyMyClass::myMethod(myArg) override {
  OPENASSETIO_PYBIND11_OVERRIDE(
      std::shared_ptr<MyReturnType>, MyClass, myMethod, myArg);
}
```

to

```c++
std::shared_ptr<MyReturnType> PyMyClass::myMethod(myArg) override {
  OPENASSETIO_PYBIND11_OVERRIDE(
      PyRetainingSharedPtr<MyReturnType>, MyClass, myMethod, myArg);
}
```

Note that the return type of the C++ member function is unchanged.

This ensures that the `shared_ptr` returned by the member function call
also keeps the Python object alive.

#### Function arguments

When binding C++ member functions as Python methods we must modify the
signature from, for example

```c++
.def("myMethod",
     [](MyClass& myObject, std::shared_ptr<MyArg> myArg, ...
```

to

```c++
.def("myMethod",
     [](MyClass& myObject, PyRetainingSharedPtr<MyArg> myArg, ...
```

for all `MyArg` types where we need to keep the incoming Python object
alive for at least as long as the `shared_ptr`.

As a convenience for decorating (member) function pointers, we have
added a `RetainPyArgs` helper, which can be used to decorate a function
such that specific `shared_ptr` arguments are converted to
`PyRetainingSharedPtr`. For example,

```c++
.def("myMethod",
     RetainPyArgs<
         std::shared_ptr<MyArg1>,
         std::shared_ptr<MyArg2>>::forFn<&MyClass::myMethod>(), ...
```

will ensure all `shared_ptr<MyArg1>` or `shared_ptr<MyArg2>` arguments
will be converted to `PyRetainingSharedPtr<MyArg1>` or
`PyRetainingSharedPtr<MyArg2>`, respectively. This is equivalent to
manually wrapping in a lambda, as shown above.

### Default arguments

pybind11 allows bound methods to have keyword arguments with default
values, for example

```c++
.def("myMethod",
     &MyClass::myMethod, py::arg("myArg") = myDefaultValue, ...
```

In general, it is not safe to set the default value to an arbitrary
user-defined type, since mutations persist to the next invocation.

However, it is safe to set the default value to a primitive type, or
C++ types that are auto-converted to/from Python native types.

In particular, many STL types are [auto-converted by
pybind11](https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html#automatic-conversion)
to/from Python native types, necessitating a copy, and are therefore
safe to use as default values.

These types include `std::string`, `std::vector<>`, `std::deque<>`,
`std::list<>`, `std::array<>`, `std::valarray<>`, `std::set<>`,
`std::unordered_set<>`, `std::map<>`, and `std::unordered_map<>`.

Note that any values within the container are subject to the same
conditions.

A more detailed explanation follows.

#### Explanation

We have to be careful with what types we use when setting default
values. This is analogous to the well-known common pitfall in pure
Python, where a keyword argument's default value is set to a mutable
type, for example

```python
def myMethod(self, myArg=set()):
  myArg.add("myValue")
```

Here, subsequent calls to `myMethod` will find that `myArg` is no longer
empty - the default value has been mutated.

A similar problem exists with pybind11 default argument values, but it
is subtly different.

When setting a default value for an argument, pybind11 will

1. Convert the default value to a Python object
2. Store the Python object in the function record.

When a C++ function is called from Python and a defaulted argument not
provided, then

1. The default value is recalled from the function record and inserted
   into the input Python arguments.
2. The standard conversions from Python arguments to C++ arguments then
   takes place.

When the default value is a generic user-defined type, the stored Python
object will contain a reference. In this case, the same problem occurs
with pybind11 as with pure Python - default values can be mutated during
a C++ function call and those mutations persist to the next invocation.

However, some C++ types are converted to/from native Python types,
including primitives such as `int` and `float`, but also (by default)
`std::string` and container types like `std::vector` (converted to
Python `list`) and `std::set` (converted to Python `set`).

In these cases, the initial conversion of the C++ default value to a
Python object (to be stored in the function record) necessitates a copy.
Similarly, the conversion back to a C++ object when the function is
called also necessitates a copy.

So for types that are converted to/from native Python types, it is safe
to assign them as default argument values.  Note that this includes
e.g. `std::vector` (Python `list`), which is _not_ safe in pure Python.

### The GIL

The GIL should be released for non-trivial bound methods using
```c++
py::call_guard<py::gil_scoped_release>{}
```
in the pybind11 `.def(...)` arguments (see [pybind11
docs](https://pybind11.readthedocs.io/en/stable/advanced/misc.html#global-interpreter-lock-gil)).
This allows other Python threads to continue while the C++ function
body runs.

Releasing the GIL also prevents deadlocks in case the C++ function body
spawns and waits on a thread that calls out to Python. This is
particularly important for methods that ultimately call out to functions
provided externally (e.g. manager plugins).

Any methods not released should be in O(1) time and guaranteed to not
cause a deadlock by calling out to python off-thread.

## Environment variables

All environment variables should be prefixed with `OPENASSETIO_`.
For example, `OPENASSETIO_LOGGING_SEVERITY`.

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment
Variable List_ page of the generated documentation.
