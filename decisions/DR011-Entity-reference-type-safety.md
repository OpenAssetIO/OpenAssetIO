# DR011 Entity reference type-safety

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @feltech
- **Approver:** @foundrytom
- **Outcome:** Use strongly-typed entity reference identifier.

## Background

The current API assumes a "honor agreement" in which the host will never
pass a string to an API call that accepts an entity reference unless it
has first run it through `isEntityReference` at least once, and that
method has returned `True` for the manager in question.

Note that this does not imply the entity reference actually corresponds
to an entity, only that it is understood and handled by a particular
manager.

This is specifically to allow a manager implementation to assume that
any input to a method that takes entity reference does not need
re-validating. This reduces runtime overhead and simplifies their
implementation.

However, this trust-based system does not preclude a host passing an
invalid identifier to a manager.

So we're faced with the question, how can we enforce that an entity
reference passed to API methods has been validated as relevant to the
target manager?

## Relevant data

See issue [#532](https://github.com/OpenAssetIO/OpenAssetIO/issues/532).

In some cases, managers may provide a prefix through `info()` that
allows the API middleware to accelerate this test when a manager
implementation is purely in Python to avoid costly GIL acquisitions.

A typical production asset-centric render may reference millions of
entity references, and each reference may well be of non-trivial length,
so references should not use memory longer than their natural scope in
the host codebase.

In theory, a host only needs to check `isEntityReference` once for any
given string/manager combination, and that string can then be used with
any other API method with that manager.

However, there is an obvious potential for host applications to break
this contract, either by not validating the reference or by validating
against the wrong manager implementation.

From this we can see there are two questions that must be answered
before we can guarantee to a manager that an entity reference is
relevant to them:

1. Is the string an entity reference?
2. Is the entity reference relevant for the target manager?

In the current API, this translates to

1. Has `isEntityReference` been called on the string?
2. Was `isEntityReference` called using the correct manager
   implementation?

The current trust-based system solves this by simply assuming the host
application will satisfy the contract. Ideally these questions could be
answered and enforced automatically, and cheaply.

One further consideration is the possibility of entity references that
are known to be valid. For example, they may have been validated at some
point in the past or in a separate process. Forcing an ultimately
pointless (if cheap) `isEntityReference` check in this case is
undesirable. Again, the current trust-based system solves this
trivially, if not robustly.

### References

#### Issues

See issue [#532](https://github.com/OpenAssetIO/OpenAssetIO/issues/532).

#### Projects

**OpenTimelineIO** has `SerializableObject::ReferenceId`, which is
deserialised from JSON objects with schema `SerializableObjectRef.1`. It
simply stores a `std::string id` field. The `id` is looked up in a
`_Resolver`'s `std::map` of `std::string` to `SerializableObject`.

They also have `ExternalReference`, which is perhaps most comparable to
an entity reference, and acts as a strong type containing a
`target_url` field, as well as metadata fields.

**USD** uses interned strings, which
has [caused some problems](https://github.com/PixarAnimationStudios/USD/issues/1287).
Their `TfToken` type is a globally interned string type for efficient
comparison, assignment, and hashing. Similarly their `SdfPath` is
analogous to entity references and, according
to [the docs](https://graphics.pixar.com/usd/dev/api/class_sdf_path.html#details)
> uses a global prefix tree to efficiently share representations of
> paths

They make specific mention of thread-safety of the global store, which
comes at a cost when creating or copying paths.

#### Articles

FluentCpp's
[Strong types for strong interfaces](https://www.fluentcpp.com/2016/12/08/strong-types-for-strong-interfaces/)
and
[Struct as strong type](https://www.fluentcpp.com/2018/04/06/strong-types-by-struct/)

## Options considered

### Option 1

Keep the current trust-based solution expecting hosts to call
`isEntityReference` before using a reference in any manager API call.

#### Pros

- Conceptually simple.
- No changes required.
- No global state.
- Assuming entity references are valid when used means zero validation
  cost in manager API methods.
- Trivial language bindings - everything supports strings.
- String types often have many built-in conveniences, e.g. native
  support for hashing (dictionaries, sets) and serialisation.

#### Cons

- Relies on trust - easy to break.
- A non-reference string argument for a function can be erroneously
  given a reference (and vice versa) and compilers/linters will not
  complain.

Estimated cost: Small

### Option 2

Strong typing: add a custom type `EntityRef` that wraps a string
reference, and require that type in all manager API calls that take (or
return) an entity reference.

Instances of the custom type can only be constructed by
`Manager.createEntityReference`, which throws an exception if the
reference is not valid.

`createEntityReference` does not need to be implemented by the manager
plugin, this is a convenience that will make use of the current API's
`isEntityReference`.

#### Pros

- Compile-time enforcement that a reference was validated. Though not
  necessarily for the appropriate manager.
- An entity reference type can contain a reference to the manager that
  generated it, allowing for (cheap) validation that a reference is
  relevant to a given manager. This could be added to all middleware
  methods as further validation.
- If independently trivially constructible, then retains the advantage
  of allowing optional circumvention of `isEntityReference`, for
  references the host is already sure of.
- No need for global state.
- Strong typing of domain concepts, avoiding "primitive obsession", is
  considered good coding practice. E.g. it prevents passing an entity
  reference to the wrong argument of a function that happens to also be
  a string.
- Extensible, open to future modification.
- Adds the possibility of implementation of references as a polymorphic
  class, allowing the manager implementation the opportunity to return a
  subclass instance bundling arbitrary additional data.

#### Cons

- Assuming the reference type can be trivially constructed without
  validation, this raises similar trust issues to just using
  strings. Mitigated by the fact that hosts must very intentionally
  do this, so it's less likely that they simply "forgot" to validate.
  Further mitigated if we enforce validation in the constructor, with
  potentially an optional `dontValidate` parameter.
- A manager may assume the string is a reference, but not that it is
  relevant to that particular manager, without further probing.
- Validation that a reference is relevant to a given manager, added to
  all middleware methods, would introduce some runtime cost. Mitigated
  by making such checks a debug-only feature, if we assume that a
  badly-behaved host is a particularly exceptional case.
- Maintenance burden of a custom type and its language bindings.
- Serialisation and transfer across processes/languages is more complex
  than using a native type that is widely understood, such as a string.

Estimated cost: Medium

### Option 3

Use an interned string type, with a per-manager database. That is, a
call to `createEntityReference` returns an index to an entity reference
string in a manager-specific database, or raises an exception if the
reference is not valid.

`createEntityReference` does not need to be implemented by the manager
plugin, this is a convenience that will make use of the current API's
`isEntityReference` (assuming the string is not already interned).

#### Pros

- Conceptually simple and intuitive as "just like a string".
- Compile-time enforcement that a reference was validated. Though not
  necessarily for the appropriate manager.
- Attempts by the manager to unpack a reference that is not meant for
  it can give an explicit, easy to understand, runtime error.
- No way to circumvent validation, removing a class of programmer error.
- Low memory overhead within a host for storage of many references to
  the same entity.

#### Cons

- Additional memory overhead of caching valid references. 1 million
  references at 100 (UTF-8) characters each is approx 100 MB.
- Assumes that the associated manager cache is always available, meaning
  either global state or indefinite lifetime of manager instances.
- No way to circumvent validation, even if the host is certain the
  reference is valid.
- Database state is not trivially available across processes, so
  entity references may need pointlessly re-validating.
- Maintenance burden of a non-native custom/third-party type and its
  language bindings.

Estimated cost: Medium

## Outcome

Option 2 was chosen. The combination of strong typing, extensibility
and lack of need for a global cache, make it the clear winner.

There are still workflow questions to be answered. However, it seems
clear that we should, at least initially, mirror the
`Manager.createContext` function with a `Manager.createEntityReference`
function.

Validation that a reference was created for the relevant manager can be
added to the middleware (enabled/disabled by a global flag).

## Appendix

### Option 2 - Usage sketch

**Host**

```python
# Assume constructible from a manager, which validates.
checked_ref: EntityReference = manager.createEntityReference(
    "ref://to.check")

# Assume constructible independently, which may or may not validate.
known_good_ref = EntityRef(manager, "ref://known.good")

refs = [checked_ref, known_good_ref]


# Resolve the refs we've got, now we're pretty sure they're all valid
# for the manager.

def success_callback(idx, traits_data):
    process_location(
        LocateableContentTrait(traits_data).getLocation())


def error_callback(idx, error):
    if error.code == kEntityResolutionError:
        # Maybe we made a mistake...
        if not refs[idx].isForManager(manager):
            # We passed the wrong ref to the wrong manager.
            # Note that this could be a check in the middleware instead.
            # Checking it here is too late, really, since a malformed
            # ref was sent to the manager.  We're just lucky we didn't
            # cause a nastier exception during `resolve`.
            raise RuntimeError(
                "Programming error! Ref resolved with wrong manager.")

    log.warn("Error resolving %s" % refs[idx])


manager.resolve(refs, {LocateableContent.kID}, context,
                success_callback, error_callback)
```

**Manager**

We assume the strongly typed `ref` `EntityReference` instance has a
`toString`-like method.

```python
def resolve(self, refs, traitSet, context, hostSession,
            success_callback, error_callback):
    for idx, ref in enumerate(refs):
        ams_data = backend.resolve(traitSet, ref.toString())
        if not ams_data:
            error_callback(
                idx, ErrorMessageAndCode("Failed to resolve",
                                         kEntityResolutionError))
        else:
            success_callback(idx, convert_to_traits_data(ams_data))
```

### Option 3 - Usage sketch

**Host**

```python
# Assume constructible from a manager, which validates.
ref: EntityReference = manager.createEntityReference("ref://to.check")


# ... Do some other work...

def success_callback(idx, traits_data):
    process_location(
        LocateableContentTrait(traits_data).getLocation())


def error_callback(idx, error):
    log.warn("No location for ref %s" % refs[idx])


try:
    # Resolve using what we hope is the same manager just bound to a
    # different variable name.
    other_manager.resolve([ref], {LocateableContent.kID}, context,
                          success_callback, error_callback)

except ManagerMismatchError:
    # Will be triggered if the manager attempts to unpack a ref that
    # was meant for a different manager.
    log.error("Programming error! Ref resolved with wrong manager.")
    return False
```

**Manager**

In order to extract the underlying string of the reference, the
`toString` method must be given a manager whose database should be
queried.

```python
def resolve(self, refs, traitSet, context, hostSession):
    for idx, ref in enumerate(refs):
        # Note: toString may raise an exception if a ref for another
        # manager was given. This is an exceptional case that should
        # never happen in a well-behaved host, so don't bother guarding
        # against it and just let any exception propagate.
        ams_data = backend.resolve(traitSet, ref.toString(self))
        if not ams_data:
            error_callback(
                idx, ErrorMessageAndCode("Failed to resolve",
                                         kEntityResolutionError))
        else:
            success_callback(idx, convert_to_traits_data(ams_data))
```
