# DR010 TraitsData value retrieval API

- **Status:** Decided
- **Impact:** Low
- **Driver:** @feltech
- **Approver:** @feltech, @foundrytom
- **Contributors:** @feltech, @foundrytom, @carmenpinto
- **Outcome:** TraitsData will use an 'out parameter' API, with an
  additional `std::optional` API to follow.

## Background

The `TraitsData` container is a generic dictionary type. It allows
arbitrary keys to be set, with values that are one of a restricted set
of simple types. The class is implemented in C++, and bound to C and
Python.

At runtime, there is no guarantee that any given key is present. It must
be simple for consuming code to handle missing values, or inspect which
values are available.

## Relevant data

`TraitsData` instances are used in high-performance API interactions,
and so their implementation may be subject to change over time as we
learn more about the performance characteristics of real-world systems.
Consequently, we desire to keep the storage implementation private to
facilitate future refactoring and/or optimization without needing to
change surrounding code.

USD (a popular library in this space, with many similar concepts) uses
an out parameter plus return status for Attribute retrieval.

- [UsdAttribute::Get](https://graphics.pixar.com/usd/release/api/class_usd_attribute.html#a9d41bc223be86408ba7d7f74df7c35a9)
- [UsdClipsAPI::GetClips](https://graphics.pixar.com/usd/release/api/class_usd_clips_a_p_i.html#a94d6e4d856cc3a92aae45953b9e942a6)

## Options considered

### Option 1: Return std::optional

```cpp
std::optional<Value> Data::get(const Key& key) const;
```

#### Pros

- More modern.
- Matches Python where `None` would be returned.
- `std::optional` is well understood by programmers so no new mechanism
  to learn.

#### Cons

- Binding to C requires wrapping of `std::optional`.
- In some of the tested use cases, added more caller-side boilerplate
  compared to option 2.
- Requires temporary allocation of the `std::optional` to return the
  value, to then be immediately unwrapped (`std::optional` may not used
  internally by the storage)

### Option 2: Out parameter with status return

```cpp
bool Data::get(Value* outValue, const Key& key) const;
```

#### Pros

- Trivial to bind to C.
- Avoids temporary allocations of a result container.
- Allows direct-assignment to existing variables.
- Access and status available through a single call.
- The return value can be extended to more detailed result code if
  needed - for example with templated type-specific access where there
  are several failure modes.

#### Cons

- Old-school design pattern.
- Python binding will take a different form (return `None`, as out
  params are un-unavailable).
- In some of the tested use cases, added more caller-side boilerplate
  compared to option 1.

## Outcome

OpenAssetIO will initially adopt the out parameter with status
return pattern, adding an additional `std::optional` variation at a
later date.

## Rationale

This approach simplifies the delivery of end-to-end functionality across
C, C++ and Python, without precluding the addition of the more modern
variant at a later date. There is strong precedent for the out param
mechanism in other well established libraries.

