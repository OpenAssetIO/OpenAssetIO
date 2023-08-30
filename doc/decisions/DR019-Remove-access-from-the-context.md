# DR019 Remove access from the Context

- **Status:** Decided
- **Impact:** High
- **Driver:** @foundrytom
- **Approver:** @feltech, @elliotcmorris, @antirotor
- **Outcome:** The `access` property will be removed from `Context` and
  made a first class parameter of relevant methods.

## Background

OpenAssetIO forms a bridge between a 'host' (tool or application) and a
'manager' (asset management system). The [interface to the
manager](https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1v1_1_1manager_api_1_1_manager_interface.html)
is considered stateless. Its methods are supplied a
[`Context`](https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1v1_1_1_context.html)
object to correlate disparate calls by the host and encapsulate the
state of the current session.

Example host pseudo-code:

```python
context = manager.createContext()
...
manager.resolve(..., context)
manager.getWithRelationship(..., context)
...
manager.resolve(..., context)
```

There are several pieces of information held by this context object:

- `access` [Required] Defines what the host intends to do
  with a specific entity in a variety of situations (read or write).
- `managerInterfaceState` [Optional] An opaque state object owned by the manager.
- `locale` [Optional] Traits (qualities) of the host environment, that the
  manager may use to inform its behaviour.

Of these, `access` is critical to ensuring the correct behaviour. For
example, an error would be raised if a host attempts to resolve an
existing immutable entity for write, or a future entity for read.

The host must carefully manage the value of the `access` property for
each API call:

```python
# Check management policy
context.access = kRead
manager.managementPolicy(..., context)
context.access = kWrite
manager.managementPolicy(..., context)
context.access = kCreateRelated
manager.managementPolicy(..., context)
...
# Loading data
context.access = kRead
data = manager.resolve(..., context)
...
# Publishing new data
context.access = kWrite
working_ref = manager.preflight(..., context)
data = manager.resolve(..., context)
...
```

The `Context` object is passed by reference (see below), and so changes
to its properties may have inadvertent side effects if it has been
shared across multiple threads. To work around this, the
`createChildContext` method allows for an isolated copy to be obtained,
for thread-local use.

```python
# Publishing new data
write_context = context.createChildContext()
write_context.access = kWrite
working_ref = manager.preflight(..., write_context)
data = manager.resolve(..., write_context)
...
```

In practical use, this approach has proven to be hard to understand and
easy to get wrong. We frequently find ourselves writing "don't forget to
consider the context" in method documentation. An API of any quality
should be intuitive to use wherever possible, and avoid reliance on
detailed examination of the docs.

The result is that a core API mechanism is largely misunderstood, and
easily overlooked.

We propose extracting the `access` property into first-class arguments
of the API methods whose behaviour it directly affects.

## Relevant data

Of the data held by the context, `managerInterfaceState` and `locale`
tend to be relatively stable, but `access` varies between API calls, and
may need to be set to different values across threads.

These properties were originally combined into the Context object to
group together all the 'host environment' description, and reduce
parameter bloat.

The context is held by reference for several reasons:

- The use of the same context object with different API calls is what
  ties these API calls to the stateless manager interface together.
- The manager state is opaque and consequently assumed non-copyable.
- We have to manage the lifetime of this object across multiple runtime
  languages, each with their own memory management models.

## Options considered

### Option 1 - Do nothing

No change, `access` remains part of the context.

#### Pros

- No code changes necessary.
- Fewer arguments to API methods.
- All data about the host environment is in one place.

#### Cons

- A critical part of the API that directly affects the behaviour is
  relatively hidden amongst stable, infrequently varying data. Requiring
  implementations on both sides to "remember to do the right thing".
- The context is passed to some methods that don't need to consider
  access, but this is not made apparent.
- As the context is often shared between threads, the possibility of
  unintended side effects when modifying `access` is high.
- Implementers are unsure when they should use `createChildContext`,
  often resulting in defensive use, which has a significant runtime
  overhead.
- The canonical behaviour for a host or manager implementations is only
  discovered through careful consideration of the documentation.
- Surfaces debate about attempting to switch `Context` to value
  semantics.

### Option 2 - Extract to argument

Extract the `access` field into a first-class argument to the relevant
methods.

A sketch of what this could look like (final design TBC):

```python
# Check management policy
manager.managementPolicy(kRead, ..., context)
manager.managementPolicy(kWrite, ..., context)
manager.managementPolicy(kCreateRelated, ..., context)
...
# Loading data
data = manager.resolve(kRead, ..., context)
...
# Publishing new data
working_ref = manager.preflight(..., context)
data = manager.resolve(kWrite, ..., context)
...
```

#### Pros

- Host implementations must consider `access` when making API calls as
  it is a required argument.
- Manager implementations don't have to remember to check `access` in
  the context as it is directly provided to the method.
- Access is not supplied to methods that don't need to consider it.
- The necessity (and ambiguity) of `createChildContext` is removed from
  the majority of host call sites. This also reduces runtime overhead
  significantly.
- Detailed memorization of the docs becomes less critical as the access
  concept is surfaced directly in the API signature. The documentation
  itself can also be more specific.
- High-churn `access` mutations are decoupled from the relatively stable
  and coherent lifetimes of the other `Context` properties.
- Removes some debate around attempting to make Context use value
  semantics to avoid the side effect issue.

#### Cons

- Increased argument count to many API methods.
- All existing plugins and integration code will need light-weight
  modifications.

## Outcome

We will extract `access` from the `Context` class, making it a
first-class argument.

### Rationale

We feel, given our current alpha status, the cost of updating existing
call sites is justified by the simplification of this critical
behavioural control mechanism.

Observations of real-world integration efforts have highlighted just how
easy it is to miss-manage the context, resulting in hard to spot
programming/logic errors. We need to make the API as robust and easy to
learn as possible (it's hard enough as it is).

This is the last opportunity we have to make a change like this before
adoption is too broad.
