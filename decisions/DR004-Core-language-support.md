# DR004 Core language support

-   **Status:** Decided
-   **Impact:** High
-   **Driver:** @foundrytom
-   **Approver:** @foundrytom @feltech
-   **Contributors:** @foundrytom @feltech @meshula
-   **Outcome:** OpenAssetIO will use `C++` as the core language for
    efficient implementation, with critical business logic exposed
    through portable `C` API.

## Background

OpenAssetIO strives to provide a universal standard for communications
between a process that consumes or produces data, and any external
systems that manage that data.

To be successful in any meaningful way, it needs to be portable to
which ever programming language(s) are meaningful to its target
audience.

At the time of writing, the majority of expected integrations are within
`C++` and/or `Python` environments. Other languages such as `Rust` or
`go` are gaining traction. Broader reaching applications of OpenAssetIO
introduce `JavaScript`, `Swift` and others.

The library must be designed to simplify integration into current
_and_ future programming environments, without the need to re-implement
critical business logic.

## Relevant data

### Required language support

`C++`, `Python`

### Projected language support

`C`, `JavaScript`, `Java`, `Swift`, `Rust`, `go`

### Bindings

Research has shown that the common denominator when addressing the above
listed languages is a `C` interface. A standard `C` API surface, with
clear and manageable ownership semantics would facilitate support in the
broadest range of future programming environments.

Ideally, any bindings would also allow idiomatic programming within
the target language, rather than forcing specific design patterns from
any internals of OpenAssetIO - such as synchronous programming, RAII,
etc.

### Performance

A core requirement raised by numerous parties is that the "happy path"
should be as performant as possible. Thus, it is required that any
mechanism introduced to broaden compatibility doesn't compromise the
(current) majority deployment scenarios.

Of note, a `C++` host talking to a `C++` manager has been the most
frequently requested high-performance pathway.

### Development lifecycle

The overhead of maintaining dynamically linked `C++` libraries within a
plugin-based architecture is often fraught with constantly chasing ABI
changes and/or conflicts between mutual dependencies.

Foundry has prior art in using `C` function pointer suites as a compiler
isolation technique on top of `C++` implementations that can help
de-couple the plugin host and the specifics of any given plugin.

In the constantly evolving landscape defining which dependency versions
are in use within which versions of common DCC tools, avoiding the need
to matrix-compile and juggle plugin search paths per-host would be
massively beneficial.

## Options considered

### Option 1

`C++` and `Python` support only.

**Estimated Cost**: Small

#### Pros

-   Simplifies development.

#### Cons

-   Leaves use within languages other than these a potentially
    challenging exercise left to the reader.
-   Compiler isolation support would need to be handled as an add-on
    through an additional layer such as a `C` suite, `protobuf` or
    similar.

### Option 2

`C` core library, bound to `C++` and `Python` as appropriate.

**Estimated Cost**: Large

#### Pros

-   Makes future bindings or adoption in `C`-based languages far
    simpler as all core API functionality is inherently available
    through idiomatic `C`.
-   Inherently presents a stable ABI isolation layer between hosts and
    plugins.

#### Cons

-   The data model of OpenAssetIO _requires_ `map` and `optional` types.
    The lack of standardization in `C` around these concepts means a
    local implementation of these would be required. This, and their
    mapping to C++ and Python introduces run-time and maintenance
    overhead, as well as increased code complexity and project risk.
-   `C` is notoriously unsafe with regards to type-safety and memory
    management. Higher-level systems programming languages, such as
    `C++` and `Rust`, add well-known idioms and/or protective mechanisms
    (both compile-time and run-time, with little or no performance
    overhead).  These can help reduce run-time or programming errors of
    this nature.
-   `C` programming idioms around required topics such as inheritance
    and generic programming use macros. The use of macros makes for
    awkward, or impossible interoperation with languages such as `C++`
    where the use of such constructs interfere with clarity and best
    practices.
-   Long-term maintenance of an extensive `C` codebase, using advanced
    techniques such as the above, is potentially more difficult due the
    deficit of low-level `C` experience in the broader project
    community.
-   Introduces additional boilerplate and overhead in the `C++` to `C++`
    high-performance path.

### Option 3

`C++` core library, with critical business logic exposed via `C`
interfaces. Bound to `Python`.

**Estimated Cost**: Medium

#### Pros

-   The `C` API is still a first-class citizen within the architecture,
    aiding future adoption in other languages and the development of
    optional ABI isolation layers.
-   The core implementation can leverage the `C++17` standard library,
    and language features, dramatically reducing code complexity.
-   The `C++` to `C++` high-performance path is natively supported.

#### Cons

-   Easy to inadvertently 'leak' `C++` specific practices through the
    `C` API.
-   The standard library can add 'bloat' when certain conveniences are
    used.

## Outcome

OpenAssetIO will adopt **Option 3** and implement the API core in `C++`.
Where this contains language-universal business logic (as opposed to
language-specific boilerplate), it will be exposed through an idiomatic
`C` interface that can be used to bind to arbitrary languages at some
future point.

The appendix contains a sketch illustration of how the implementation of
a typical API component may look.

## Rationale

This arrangement provides the best possible intersection of the
requirements outlined in the Relevant data section.

-   The `C++` to `C++` fast path can be implemented directly with
    minimal middleware, at the expense of ABI coupling/etc.
-   Compiler/memory isolation via a `C` function pointer suite, or other
    technique such as `protobuf` can be implemented as required via a
    shim between a host and a plugins implementation on top of the
    underlying `C++` core.
-   Future language bindings should be more readily implementable as the
    `C` interface is part of the core design, rather than an
    afterthought.
-   The core code base can make maximum use of standard library
    containers and memory management tools, reducing entire categories
    of programming errors.


## Appendix - an implementation sketch

The code segment below illustrates a working sketch of a potential
approach to a typical core component implementation.

> Note: The exact semantics of string handling, and the extended details
> of the opaque handle + access API for data types exposed through `C`
> will be finalized and detailed in future documentation.

```cpp
#include <cstring>
#include <memory>
#include <string>
#include <unordered_map>

////////////////////////////////////////////////////////////////////////
// In a common header somewhere

#define OpenAssetIO_VERSION v0_0
#define OpenAssetIO_C_NAMESPACE(thing) openassetio_##OpenAssetIO_VERSION##thing##_

////////////////////////////////////////////////////////////////////////
// Utility to create/release/convert C++ <-> C

namespace openassetio
{
struct CHandle
{
    template <class Class>
    using Ptr = std::shared_ptr<Class>;

    template <class Class, class Handle, class... Args>
    static Handle create(Args &&... args)
    {
        try
        {
            auto pp = new Ptr<Class>;
            *pp = std::make_shared<Class>(std::forward<Args &&>(args)...);
            return reinterpret_cast<Handle>(pp);
        }
        catch (...)
        {
            return nullptr;
        }
    }

    template <class Class, class Handle>
    static void release(Handle handle)
    {
        auto pp = reinterpret_cast<Ptr<Class> *>(handle);
        delete pp;
    }

    template <class Class, class Handle>
    static Ptr<Class> & to_cpp(Handle handle)
    {
        return *reinterpret_cast<Ptr<Class> *>(handle);
    }

    template <class Handle, class Class>
    static Handle borrow_to_c(Ptr<Class> const & p)  // Note: must `release()` when done.
    {
        auto pp = new Ptr<Class>{p};
        return reinterpret_cast<Handle>(pp);
    }
};  // namespace CHandle
}  // namespace openassetio

////////////////////////////////////////////////////////////////////////
// StringMap

namespace openassetio
{
inline namespace OpenAssetIO_VERSION
{
using StringMap = std::unordered_map<std::string, std::string>;
}
}  // namespace openassetio

#define ns(thing) OpenAssetIO_C_NAMESPACE(thing)

extern "C"
{
    // Opaque C handle to a pointer to a shared_ptr to a StringMap
    typedef struct ns(StringMapOpaque) * ns(StringMapHandle);

    // Create
    ns(StringMapHandle) ns(StringMap_create)()
    {
        using openassetio::CHandle;
        using openassetio::StringMap;
        return CHandle::create<StringMap, ns(StringMapHandle)>();
    }

    // Release
    void ns(StringMap_release)(ns(StringMapHandle) handle)
    {
        using openassetio::CHandle;
        using openassetio::StringMap;
        CHandle::release<StringMap>(handle);
    }

    // Setter
    void ns(StringMap_set)(ns(StringMapHandle) handle, const char * key, const char * val)
    {
        using openassetio::CHandle;
        using openassetio::StringMap;
        auto & ptrStringMap = CHandle::to_cpp<StringMap>(handle);
        ptrStringMap->insert({key, val});
    }
}

////////////////////////////////////////////////////////////////////////
// Dummy Manager declaration

#undef ns
#define ns(thing) OpenAssetIO_C_NAMESPACE(hostAPI_##thing)

namespace openassetio
{
inline namespace OpenAssetIO_VERSION
{
namespace hostAPI
{
struct Manager
{
    void updateTerminology(StringMap & terminology) const;
    std::string displayName() const;
};
}  // namespace hostAPI
}  // namespace OpenAssetIO_VERSION
}  // namespace openassetio
extern "C"
{
    typedef struct ns(ManagerOpaque) * ns(ManagerHandle);
}

////////////////////////////////////////////////////////////////////////
// Default terminology

#undef ns
#define ns(thing) OpenAssetIO_C_NAMESPACE(terminology_##thing)

extern "C"
{
    [[maybe_unused]] static const char * ns(kTerm_Asset) = "asset";
    [[maybe_unused]] static const char * ns(kTerm_Assets) = "assets";
    [[maybe_unused]] static const char * ns(kTerm_Manager) = "manager";
    [[maybe_unused]] static const char * ns(kTerm_Publish) = "publish";
    [[maybe_unused]] static const char * ns(kTerm_Publishing) = "publishing";
    [[maybe_unused]] static const char * ns(kTerm_Published) = "published";
    [[maybe_unused]] static const char * ns(kTerm_Shot) = "shot";
    [[maybe_unused]] static const char * ns(kTerm_Shots) = "shots";
}
namespace openassetio
{
inline namespace OpenAssetIO_VERSION
{
namespace terminology
{
const StringMap defaultTerminology{
    {ns(kTerm_Asset), "entity"}, {ns(kTerm_Published), "written"},
    // ... etc
};
}
}  // namespace OpenAssetIO_VERSION
}  // namespace openassetio
extern "C"
{
    // Getter
    const char * ns(get_default_term)(const char * key)
    {
        // Static, so safe to return raw pointer.
        return openassetio::terminology::defaultTerminology.at(key).c_str();
    }
}
////////////////////////////////////////////////////////////////////////
// Mapper class

namespace openassetio
{
inline namespace OpenAssetIO_VERSION
{

namespace terminology
{

std::string replaceTerms(const StringMap & terminology, const std::string & sourceStr)
{
    // ...format the string...
    (void)terminology;
    return sourceStr;
}

class Mapper
{
public:
    explicit Mapper(const hostAPI::Manager & manager, StringMap terminology = defaultTerminology)
        : m_terminology{std::move(terminology)}
    {
        manager.updateTerminology(m_terminology);
        m_terminology[ns(kTerm_Manager)] = manager.displayName();
    }

    std::string replaceTerms(const std::string & sourceStr)
    {
        return terminology::replaceTerms(m_terminology, sourceStr);
    }

private:
    StringMap m_terminology;
};

}  // namespace terminology
}  // namespace OpenAssetIO_VERSION
}  // namespace openassetio

////////////////////////////////////////////////////////////////////
// Mapper C binding

extern "C"
{
    typedef struct ns(MapperOpaque) * ns(MapperHandle);

    ns(MapperHandle) ns(Mapper_create)(OpenAssetIO_C_NAMESPACE(hostAPI_ManagerHandle) hManager)
    {
        using openassetio::CHandle;
        using openassetio::hostAPI::Manager;
        using openassetio::terminology::Mapper;

        // By-reference means we're "stealing" the pointer (but not for
        // long). If we remove the `&` then we "borrow" - incrementing
        // the ref count.
        auto const & ptrManager = CHandle::to_cpp<Manager>(hManager);

        return CHandle::create<Mapper, ns(MapperHandle)>(*ptrManager);
    }

    void ns(Mapper_release)(ns(MapperHandle) hMapper)
    {
        using openassetio::CHandle;
        using openassetio::terminology::Mapper;
        CHandle::release<Mapper>(hMapper);
    }

    void ns(Mapper_replaceTerms)(
        ns(MapperHandle) hMapper, char const * sourceStr, char * out, int maxlength)
    {
        using openassetio::CHandle;
        using openassetio::terminology::Mapper;

        auto const & ptrMapper = CHandle::to_cpp<Mapper>(hMapper);

        auto result = ptrMapper->replaceTerms(sourceStr);

        std::strncpy(out, result.c_str(), static_cast<size_t>(maxlength));
    }
}

// ... or ...

////////////////////////////////////////////////////////////////////
// Without Mapper C binding - rewrite Mapper in target language if
// necessary, calling through to this core logic.

extern "C"
{
    OpenAssetIO_C_NAMESPACE(StringMapHandle) ns(defaultTerminology)()
    {
        using openassetio::CHandle;
        using openassetio::StringMap;
        using openassetio::terminology::defaultTerminology;
        // Take a copy of static defaultTerminology and return a
        // (pointer to a) shared_ptr of it. So must be
        // `StringMap_release`d when done.
        return CHandle::create<StringMap, OpenAssetIO_C_NAMESPACE(StringMapHandle)>(
            defaultTerminology);
    }

    void ns(replaceTerms)(
        OpenAssetIO_C_NAMESPACE(StringMapHandle) hTerminology,
        char const * sourceStr,
        char * out,
        int maxlength)
    {
        using openassetio::CHandle;
        using openassetio::StringMap;

        auto const & ptrTerminology = CHandle::to_cpp<StringMap>(hTerminology);

        auto result = openassetio::terminology::replaceTerms(*ptrTerminology, sourceStr);

        std::strncpy(out, result.c_str(), static_cast<size_t>(maxlength));
    }
}
```
