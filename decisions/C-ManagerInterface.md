# Initial C API Proposal

This proposal is scoped to the C API bindings for the minimal 
`ManagerInterface` methods that have been ported to C++ to date, 
specifically `identifier()` and `displayName()`. Despite this tight
restriction in scope there are several design decisions to be addressed.

## Namespacing

In C, exported symbols must be namespaced by prefixing the symbol name
with some string.

Since our top-level namespace includes a version tag, which is likely to
change, we must use a macro to ease maintenance, e.g.

```c++
#define OPENASSETIO_NS(symbol) ...
```
such that `OPENASSETIO_NS(MyStruct)` expands to 
`openassetio_v0_0_MyStruct`.

## Strings

Taking inspiration from [this conversation](https://github.com/TheFoundryVisionmongers/OpenAssetIO/pull/194#discussion_r794047468)
we can bundle a string buffer and length in a single C struct for error
messages and parameters, e.g.

```c++
typedef struct {
  const size_t maxSize;
  char* buffer;
  size_t usedSize;
} OPENASSETIO_NS(SimpleString);
```
`usedSize` is for optimisation and safety and can technically be removed
if we're happy to assume null-termination and accept the performance
implications.

## Opaque handles

The opaque handle pattern used commonly in C APIs involves an arbitrary
pointer to some user data, often coded simply as a `void*`. To add some
meagre type safety, we can define an opaque handle as a pointer to an
incomplete and ultimately unused class. We then `reinterpret_cast` it 
to/from our actual pointer type on the C++ side. E.g.

```c++
typedef struct OPENASSETIO_NS(managerAPI_ManagerInterface_t) *
    OPENASSETIO_NS(managerAPI_ManagerInterface_h);
```

The type `managerAPI_ManagerInterface_t` is never used in practice, its
name is unimportant (but obviously cannot conflict with other symbols).
It is the `managerAPI_ManagerInterface_h` "handle" (pointer) type that
we will `reinterpret_cast` to/from.

## Function pointer suites

Once we have a handle to our instance, we need functions that take a 
handle as a parameter, operate on it, then potentially return a 
value or error. 

These can be defined as top-level functions exported as independent
symbols, appropriately namespaced.  

An alternative is to bundle the functions related to a particular handle
type into a struct of function pointers, which we call a function 
pointer _suite_.

Such suites have a few advantages
* Aesthetically, a struct of function pointers mirrors a class with
  methods, and if the suite is providing a C API to a C++ class then
  mentally mapping one to the other is straightforward.
* Only the suite type needs namespacing, the "methods" are simply
  struct members, which reduces code verbosity.
* Since a suite is an instance of a struct, it must be provided by
  a function call, allowing the provider a great deal of flexibility
  in its construction, compared to link-time defined symbols.
* The suite is an object that can be passed around, including as input
  to a wrapper C++ class (see below).
* In C++ the suite's functions can be implemented as a series of 
  (non-capturing) lambdas, keeping related code grouped together.

### Return values and errors

C++ functions may or may not return a value and may or may not throw an
exception. C doesn't have exceptions, so to distinguish different error
types we must use another mechanism. Commonly (and used here) this is
via (integer) error codes. 

Given this, a C API function wrapping a C++ class method has between 0
and 3 possible output values, depending on whether a return value is
expected and whether an error code and message (i.e. exception) is
possible.

The proposed signature is then
```
<error code> <namespaced function>(
    <error string out ptr>, 
    <return value out ptr>, 
    <opaque handle>, 
    <method arguments>...)
```

This has the advantage of reading similarly to a C++ function call,
with return values first, followed by the `this` pointer (handle), 
then function arguments.

Alternative, perhaps equally valid, argument orderings are of course
possible.

## ManagerInterface suite

For our oversimplified `ManagerInterface` whose only methods are 
`identifier` and `displayName`

```c++
typedef struct {
  void (*dtor)(OPENASSETIO_NS(managerAPI_ManagerInterface_h));

  int (*identifier)(OPENASSETIO_NS(SimpleString) *,
                    OPENASSETIO_NS(SimpleString) *,
                    OPENASSETIO_NS(managerAPI_ManagerInterface_h));

  int (*displayName)(OPENASSETIO_NS(SimpleString) *,
                     OPENASSETIO_NS(SimpleString) *,
                     OPENASSETIO_NS(managerAPI_ManagerInterface_h));
} OPENASSETIO_NS(managerAPI_ManagerInterface_s);

```

Note that in this case there is a `dtor` (destructor) function but no
corresponding constructor. For the particular case of `ManagerInterface`
we would expect a manager plugin to provide a `ManagerInterface_h`
handle (the details of the plugin system are out of scope here).

## C++ wrapper

A sketch is shown below. For brevity only the `identifier` member 
function is shown since the implementation of `identifier` and 
`displayName` are almost identical.

To translate an error coming from C we can define a common mapping of
error codes/messages to C++ exceptions. Below this is assumed to be
implemented in a `throwIfError` function (omitted for brevity).

```c++
constexpr size_t kStringBufferSize = 500;

// Constructor expects to be supplied a valid handle and suite.
CManagerInterface::CManagerInterface(
    OPENASSETIO_NS(managerAPI_ManagerInterface_h) handle,
    OPENASSETIO_NS(managerAPI_ManagerInterface_s) suite)
    : handle_{handle}, suite_{suite} {}

// Destructor calls suite's `dtor` function.
CManagerInterface::~CManagerInterface() { suite_.dtor(handle_); }

Str CManagerInterface::identifier() const {
  // Buffer for error message.
  char errorMessageBuffer[kStringBufferSize];
  // Error message.
  OPENASSETIO_NS(SimpleString)
  errorMessage{kStringBufferSize, errorMessageBuffer, 0};

  // Return value string buffer.
  char outBuffer[kStringBufferSize];
  // Return value.
  OPENASSETIO_NS(SimpleString) out{kStringBufferSize, outBuffer, 0};

  // Execute corresponding suite function.
  const int errorCode = suite_.identifier(&errorMessage, &out, handle_);

  // Convert error code/message to exception.
  throwIfError(errorCode, errorMessage);

  return {out.buffer, out.usedSize};
}
```

## Directory structure

The proposed directory structure is the following
```
src/openassetio-core-c
├── CMakeLists.txt
├── include
│   └── openassetio
│       └── c
│           ├── errors.h
│           ├── managerAPI
│           │   └── ManagerInterface.h
│           ├── ns.h
│           └── SimpleString.h
└── private
    ├── CManagerInterface.cpp
    ├── CManagerInterface.hpp
    └── errors.hpp
```

* There is a (optional) build target for creating a separate C library
  that links to the C++ core library.
* Public C headers are referenced via an `openassetio/c/...` path, where
  `...` mirrors the C++ namespace of the wrapped types, if appropriate.
* The `CManagerInterface` class is a private implementation detail.
