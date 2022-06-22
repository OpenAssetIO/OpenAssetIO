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

C++ classes that represent system components with reference semantics
(as opposed to 'value' types) should inherit
`std::enable_shared_from_this` and define a peer `Ptr` alias using
`std::shared_ptr`.

```cpp
class MyClass : std::enable_shared_from_this<MyClass> { ... };
using MyClassPtr = std::shared_ptr<MyClass>;
```

This is to simplify memory management across the complex range of
language bindings within the project.

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

## Environment variables

All environment variables should be prefixed with `OPENASSETIO_`.
For example, `OPENASSETIO_LOGGING_SEVERITY`.

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment
Variable List_ page of the generated documentation.
