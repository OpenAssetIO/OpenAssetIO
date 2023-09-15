# DR022 Default method implementations

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @elliotcmorris
- **Approver:** @foundrytom @felltech @elliotcmorris
- **Contributors:** @LindaWHogg @ChrisBeckfordFoundry @aelitonsilva-nuke
  @meshula
- **Outcome:**  Default implementations will throw, and suitable
  introspection provided.

## Background

The OpenAssetIO API has several optional methods, which may not be
implemented by a manager.

For example, a read-only manager does not need to implement publishing
functionality. Some managers may not support querying related entities.

We need to provide a default implementation for these methods that
exhibit suitable and consistent behaviour. There are several options
here - this DR explores these and determines which should be used.

This decision actually surfaced several interesting questions:

- Is it a runtime error if an optional method is not implemented?
- If a host does care about whether a method is implemented or not, is
  the call site the place it cares? Is a robust, independent mechanism
  for determining this preferable - as it allows higher-level logic
  changes and UX adaption?
- Should the outcome here apply to all methods or just ones where the
  host may need to adapt behaviour (for example, excluding simple
  informational methods such as `info`).

## Relevant data

- Historically, optional API methods have provided 'empty' data from
  their default implementations, eg. `getWithRelationship` supplies a
  pager with no results. This was found to simplify host code during
  prototyping. The ability to differentiate between no data and not
  implemented  was either not necessary, or `managementPolicy` was used
  ahead of time. However, the number of workflows considered was
  relatively small.

- We don't currently have a method-level introspection mechanism in the
  core API to determine if a method has been implemented or not.

- A host may use the `managementPolicy` method of the Manager to enquire
  as to what high-level functionality is supported. For example, by
  querying the policy for a particular relationship trait set, the host
  can determine whether the manager supports that relationship. This
  allows the host to know in advance whether certain methods can be
  expected to yield data - which implies implementation.

- The `managementPolicy` method does not directly correlate to specific
  API methods. It is more about classes of interaction. For example,
  querying an entity trait set for read, informs what traits can be
  resolved for that type of entity. Querying for write informs how the
  manager wishes to handle publishing - affecting the use of `prefight`,
  `resolve` and `register`.

- `managementPolicy` traits could be added to the core API to cover
  introspection of the support for additional/specific methods.

- The use of `managementPolicy` before calling an API method is not
  a requirement.

## Options considered

> **Note:** Regardless of the option chosen, we could extend
> introspection capabilities, to help mitigate some call-site
 complexity or visibility considerations.

### Option 1 - Return empty data

Default implementations of query methods would return empty data or null
optionals, and hosts would have to rely on introspection mechanisms if
they need to know whether the method has been implemented or not.

Write operations would need to pick from Option 2 or Option 3.

#### Pros

- Simplifies host code paths where the exact reason for empty data is
  not critical to control flow, as there is no additional failure case due
  to a particular plugin implementing a method or not.
- Consistent across callback-based and direct return  methods (i.e.
  `getRelatedReferences` and `info`).

#### Cons

- The host is unable to determine if the method was implemented or not
  at the call site, without an additional check of the capabilities
  API. This may mask programming errors in cases where the host
  intended to adapt their behaviour.
- Unsuitable for write operations.

### Option 2 - `NotImplemented` exception

Default implementations throw a `NotImplemented` exception.

#### Pros

- Succinctly expresses that this is an un-changeable situation and is
  unrelated to method inputs.
- Provides call-site information about implementation status.
- Encourages good host design around/use of the introspection API.
- Works with all methods types.

#### Cons

- Exceptions should be used for exceptional situations, and this one is
  potentially very common.
- Complicates host control flow and/or forces the use of `try`/`except`
  at the call site where the exact reason for empty data is not critical
  to control flows.

### Option 3 - Error with a `kNotImplemented` BatchElementError

Default implementations of batch methods would trigger the error
callback with a `kNotImplemented` batch element error code.

Direct return methods would need to pick from Option 1 or Option 2.

#### Pros

- Provides call-site information about implementation status.
- Uses existing error pathways.

#### Cons

- The method not being implemented is not strictly a batch-element
  error. It is constant for any given manager and unrelated to method
  input data.
- Can't be used with direct-return methods.
- Adds complexity to host code paths where the exact reason for empty
  data is not critical to control flow as:
  - The error callback will be invoked when the manager has not
    implemented the method.
  - Forces `try`/`except` at the call site when conveniences wrappers
    are used that convert batch element errors to exceptions.

## Decision

OpenAssetIO will adopt Option 2 - and default implementations will throw
a `NotImplementedError`.

To offset the additional complexity this brings, a simple and convenient
introspection mechanism will be introduced that will allow for
low-overhead checks to be made by the host to avoid requiring any
additional/intrusive exception handing at the call site.

> **Note:**
> We may opt to only apply this to entity-related methods for
> simplicity, making peripheral methods such as `info`, `settings`,
> `flushCaches` or similar default to no-ops to simplify API
> configuration.

### Rationale

Despite the noted cons, we believe this offers the best balance overall:

- Consistency between methods (other options only work for a specific
  sub-set).
- Does not use existing mechanisms in contentious ways.
- Separates invariant behaviour from input-specific runtime topics.
- Introspection is required anyway, as it allows hosts to adapt
  functionality ahead of time.
- The use of introspection in host code generally results in easier to
  understand logic, with a lower maintenance overhead compared to
  splitting the 'happy path' across success and error cases with
  traditional error handling.

There is the danger that the introspection mechanism is not robust, and
may be prone to programming errors by the manager.
We hope careful consideration of its design can mitigate this to an
acceptable degree.

### Example

A capability check must be determined in a single, low-cost
function call, such that it can trivially be used in a conditional.
`managementPolicy` has too much complexity and is incorrectly
parameterized for this task.

The final design needs careful thought but, we believe the resulting
mechanism may look something like this (following on from the appendix
examples using the conveniences):

```python
if (
    manager.implements(kDefaultEntityReferences)
    and ref := manager.defaultEntityReference(...)
):
    publish_to(ref)
else:
    ask_user_for_ref()
```

## Appendix

### Example - An "indifferent" host

In this example, a host is attempting to query a default entity
reference.

The `defaultEntityReference` method provides an entity reference, that
can be used by the host if the Manager is able to supply one based on
the specified entity traits. There are many cases where a default
reference may not be available, and so the returned value is an
`std::optional` (C++) or `None` (Python).

In this example, the host is indifferent to the reason for a lack of
default reference. It also illustrates potential scenarios where the
host hasn't checked capability first, or chooses not to.

The pseudocode snippets illustrate the impact of each option on the
implementation.

Regardless of which choice is made here, If we choose to fill in the
gaps with introspection it would always be possible to determine ahead
of time whether a manager has implemented the methods in question,
allowing the 'not implemented' error case to be avoided entirely.

#### Option 1 - Empty data

```python
def on_success(idx, result):
    if result:
        publish_to(result)
    else:
        ask_user_for_ref()

def on_error(idx, error):
    raise RuntimeError(error.message)

manager.defaultEntityReference({some_trait_set}, kWrite, on_success, on_error)
```

Of if a convenience signature is used:

```python
if ref := manager.defaultEntityReference(some_trait_set, kWrite)
    publish_to(ref)
else:
    ask_user_for_ref()
```

#### Option 2 - Exceptions

```python
def on_success(idx, result):
    if result:
        publish_to(result)
    else:
        ask_user_for_ref()

def on_error(idx, error):
    raise RuntimeError(error.message)

try:
    manager.defaultEntityReference(some_trait_set, kWrite, on_success, on_error)
except NotImplementedError:
    ask_user_for_ref()
```

Of if a convenience signature is used:

```python
try:
    if ref := manager.defaultEntityReference(some_trait_set, kWrite)
        publish_to(ref)
    else:
        ask_user_for_ref()
except NotImplementedError:
    ask_user_for_ref()
```

#### Option 3 - Batch element error

```python
def on_success(idx, result):
    if result:
        publish_to(result)
    else:
        ask_user_for_ref()

def on_error(idx, error):
    if error.code = kNotImplemented:
        ask_user_for_ref()
    else:
        raise RuntimeError(error.message)

manager.defaultEntityReference({some_trait_set}, kWrite, on_success, on_error)
```

If an exception convenience signature is used, this ends up being the same as
the Option 2:

```python
try:
    if ref := manager.defaultEntityReference(some_trait_set, kWrite)
        publish_to(ref)
    else:
        ask_user_for_ref()
except NotImplementedBatchElementException:
    ask_user_for_ref()
```

If a variant convenience signature is used:

```python
ref_or_error = manager.defaultEntityReference(some_trait_set, kWrite, kVariant)

if isinstance(ref_or_error, BatchElementError):
    if ref_or_error.code == kNotImplemented
        ask_user_for_ref()
    else:
        raise RuntimeError(ref_or_error.message)
else if ref_or_error:
    publish_to(ref_or_error)
else:
    ask_user_for_ref()
```
