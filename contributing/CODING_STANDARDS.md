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

## C++

### Classes

#### Smart pointers

C++ classes that represent system components with reference semantics
(as opposed to 'value' types) should inherit
`std::enable_shared_from_this` and define a peer `Ptr` alias using
`std::shared_ptr`. Their constructors should be private, and a static
`make` method provided.

This is to simplify memory management across the complex range of
language bindings within the project.

There is a convenience macro `OPENASSETIO_DECLARE_PTR` available in
`typedefs.hpp` that should be used to declare the `shared_ptr`. A macro
gives us a single point of change should we wish to alter or add more
declarations.

Usage example:

```cpp
namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace managerApi {

OPENASSETIO_DECLARE_PTR(Host)

class OPENASSETIO_CORE_EXPORT Host final {
public:
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
  PYBIND11_OVERRIDE(
      std::shared_ptr<MyReturnType>, MyClass, myMethod, myArg);
}
```
to
```c++
std::shared_ptr<MyReturnType> PyMyClass::myMethod(myArg) override {
  PYBIND11_OVERRIDE(
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

## Environment variables

All environment variables should be prefixed with `OPENASSETIO_`.
For example, `OPENASSETIO_LOGGING_SEVERITY`.

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment
Variable List_ page of the generated documentation.
