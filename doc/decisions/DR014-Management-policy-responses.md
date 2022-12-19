# DR014 Management Policy responses

- **Status:** Decided
- **Driver:** @foundrytom
- **Approver:** @feltech @ecmorris @antirotor @mattdaw
- **Outcome:** A Manager should additionally imbue a `managementPolicy`
  response with the traits that it is capable of resolving/persisting
  for each trait set.

## Background

The ability for a host to query a manager's capabilities and intent is a
critical part of the OpenAssetIO abstraction.

OpenAssetIO classifies entities (assets) using a Trait Set, which lists
one or more Traits that describe its nature. For example, an image file
may have the trait set `{'file', 'image', 'colorManaged'}` (formally
established by the `ImageSpecification` definition). The Trait Set for
an Entity can be queried using the manager's `entityTraits` method.

Some traits may have associated properties. The values for these can be
retrieved for any given entity reference using the `resolve` method.
This populates a `TraitsData` instance with the data for each requested
Trait, if available.

The `managementPolicy` method is a high-level (i.e. not entity specific)
query that a host can use to determine a manager's behaviour and ability
to resolve (or persist using `register`) trait property data in relation
to a specific trait set.

The response to this query is commonly used by a host to conditionally
enable user-facing functionality based on the behaviour or capabilities
of the specific manager that was queried.

This mechanism is flexible, and so exactly how a manager should
implement its response is potentially ambiguous. This document outlines
the rationale behind the motivation for the defined canonical behaviour.

## Relevant data

Documentation pertaining to the OpenAssetIO data model:

- [Entities, Traits and Specifications overview](../doxygen/src/EntitiesTraitsSpecifications.dox)
- [Compositional data model decision record](./DR007-Hierarchical-or-compositional-traits-for-specifications.md)
- [Unified Entity data model decision record](./DR008-Unify-the-entity-data-model.md)

Notable points:

- A Trait is how OpenAssetIO describes a behaviour or quality.
- Traits consist of a unique ID, and zero or more simple-typed
  properties that further describe that trait.
- A Trait Set is an un-ordered collection of unique trait IDs.
- Trait sets combine multiple traits to increase specificity, rather
  than meaning "or".
- A `TraitsData` instance is a dict of dicts, that can be "imbued" with
  zero or more traits and the values for any associated properties those
  traits may have. The top-level keys of this container form a Trait
  Set.
- The `managementPolicy` result is a `TraitsData` instance for each
  supplied Trait Set.
- Some managers may only care about certain specific Traits (such as
  those describing the asset's content disposition), and handle all
  'derivative entity types' the same.
- The `managementPolicy` query is not a required pre-requisite in the
  use of `resolve`, et. al. but is used to adapt application behaviour
  to improve user experience.
- Resolvable traits (i.e. those that hold Entity-specific data) should
  always have properties. Property-less traits should only be used as
  classifiers or it is not possible to tell the difference between
  missing data and non-applicable traits.

## Illustrative scenario

Consider a manager that manages the files for assets used in 2D
compositing.

It happily manages the node graphs used to define a comp, plus any
associated images read/written by the process. It does however, have
no interest in managing intermediate cache files that may be used
to speed up interactivity.

Its implementation pivots all behaviour around two (imaginary) traits:

- The `file` trait - indicating the entity's data is stored in a file.
- The `cache` trait - indicating that the data is re-creatable.

The manager has a fairly simple database and isn't capable of storing
arbitrary data for an entity, just the appropriate file path. This
means that it would only ever be able to provide data for the `file`
trait.

A host that manages several file-based Entities (e.g. its main document
and assorted data files that it reads/writes), will query the manager's
`managementPolicy` to determine for which of these the Manager should be
involved with, and what trait property data it supports.

If a Manager opts-out of managing any given trait set, then the host
will use its native UI/workflows for browsing and saving, if it opts-in,
and is capable, then it will delegate UI and data locality
responsibilities to the manager.

So, how should the manager described above respond to the
`managementPolicy` query for any specific trait set?

Lets explore the scenario where the Host is querying the manager's
policy for its native document format, and for images it generates, and
its temporary image cache:

```python
traitSets = [
    { 'file', 'nodeGraph' },                        # Main document
    { 'file', 'image', 'colorManaged' }             # Generated images
    { 'file', 'image', 'latlong', 'colorManaged' }  # Generated maps
    { 'file', 'image', 'cache' }                    # Temporary cache
]
```

Keep in mind, that the manager is only interested in `file` based
Entities, and needs to be able to explicitly opt-out of certain Trait
Sets (those that are for caches).

It applies the sweeping behaviour that any kind of `cache` should be
ignored, and anything with a `file` Trait should be managed.

## Options considered

### Option 1 - Any Matching

The manager should respond on the basis of matching any of the traits in
the set, even if it doesn't understand many others, unless it explicitly
needs to opt-out for some specialisation (not illustrated):

```python
if CacheTrait.kId in traitSet:
    continue
if FileTrait.kId in traitSet:
    ManagedTrait.imbueTo(policy)
```

Such that it opts-in to managing all Entities with the file Trait in
their set, aside from caches:

```python
policies = [
    { 'managed': {...} },  # Main document
    { 'managed': {...} },  # Generated images
    { 'managed': {...} },  # Generated maps
    {},                    # Temporary cache
]
```

Any other queries for trait sets without the file trait would be empty
`{}` indicating un-managed status.

#### Pros

- Hosts can query specific and precise trait sets, but the manager does
  not need to worry about all possible permutations.

#### Cons

- There is no way for a host to determine what traits can be resolved
  (or persisted) for any given entity, and so must tolerate missing data
  at a later date (e.g. the color space for the `colorManaged` trait, if
  the manager can't ever provide this).

### Option 2 - Exact Matching

The manager should respond only to sets where it is capable of resolving
or persisting all of the requested trait set:

```python
if traitSet == { FileTrait.kId }:
    ManagedTrait.imbueTo(policy)
```

Such that it _only_ opts into managing the specifically limited trait
set that it can support:

```python
policies = [
    {},  # Main document
    {},  # Generated Images
    {},  # Generated maps
    {}   # Temporary caches
]
```

The Host would receive empty responses (`{}`) for all of the original
trait sets, and so must potentially decompose and re-try its queried
trait sets to reveal some supported sub-set. For example, if ultimately
it just needed the file path, it could try these combinations:

```python
traitSets = [
    { 'file', 'nodeGraph' },
    { 'file', 'image', 'colorManaged' },
    { 'file', 'image' },
    { 'file', 'image', 'latLong', 'colorManaged' },
    { 'file', 'image', 'latLong' },
    { 'file', 'cache' },
    { 'file' }
]
```

Resulting in:

```python
policies = [
    {},
    {},
    {},
    {},
    {},
    {},
    { 'managed': {...} }
]
```

#### Pros

- Conveys only what traits are supported to the host, allowing
  behaviour to be properly adapted to the manager's capabilities.

#### Cons

- No way to know that actually the manager was interested in managing
  all but one of the requested trait sets.
- Host implementation is significantly more complicated.
- No way to hint at any additional traits that may be resolvable
  outside the typing trait set.

### Option 3 - Supported Traits Response

Along with the entity Trait Set, the host should also include any
additional traits that it may attempt to resolve in the future, further
specialising it. e.g. if it supported the ability to customise the file
format used for writing images, or cache lifetime by resolving a custom
trait:

```python
traitSets =[
    { 'file', 'nodeGraph' },
    { 'file', 'image', 'colorManaged', 'fileFormatOptions' }
    { 'file', 'image', 'latLong', 'colorManaged', 'fileFormatOptions' }
    { 'file', 'cache', 'retention' }
]
```

The manager should respond as per Option 1, but in addition, imbue any
of the  traits in the input trait set that the manager is capable of
resolving (read context) or persisting (write context) data for:

```python
if CacheTrait.kId in traitSet:
    continue
if FileTrait.kId in traitSet:
    ManagedTrait.imbueTo(policy)
    FileTrait.imbueTo(policy)
```

This would then look like the following:

```python
policies = [
    { 'managed': {...}, 'file': {} },  # Main document
    { 'managed': {...}, 'file': {} },  # Generated images
    { 'managed': {...}, 'file': {} },  # Generated maps
    {}                                 # Temporary caches
]
```

This indicates that the manager would like to handle interactions for
entities with all except the cache traits set, but it can only resolve
the `file` trait for these.

> Note:
> We keep the concept of additionally imbuing the `managed` trait
> (though it may seem superfluous, as an empty trait set is equivalent to
> un-managed) as in practical use cases it may well have other properties
> that cover topics such as exclusivity/etc.
> There are also additional traits that may be imbued by the manager to
> determine how it handles various aspects of the publishing process,
> e.g. thumbnails.

#### Pros

- Hosts can query specific and precise trait sets, but the manager does
  not need to worry about all possible permutations.
- Explicit communication of exact capabilities, so hosts and managers
  can suitably adapt behaviour.
- Facilitates functional workflows where the result of `managementPolicy`
  can be passed as the requested trait set for `resolve`.
- Standard Trait/Specification view classes can be used with the
  resulting `TraitsData` instance to introspect capabilities.

#### Cons

- Implementation in the manager and host may be slightly more involved
  than other options in some scenarios in order to parse the additional
  data in the response.
- Ambiguity as to whether traits with no properties should be imbued in
  the response.

## Outcome

The `managementPolicy` mechanism should always be queried with the full
trait set for any given entity specification, and any additional traits
a host may attempt to resolve/publish for that type should be added as a
specialisation (if known).

The response populated by a manager should include all
resolvable/persisted traits from that set, along with any additional
traits that describe the manager's behaviour. Traits with no properties
do not need to be imbued (see below).

## Rationale

Option 3 (chosen) provides the highest quality information to both hosts
and managers, whilst keeping the additional programming overhead to a
minimum. It allows both parties to adapt their business logic in an
explicit and coordinated fashion.

Option 1 conveys which trait sets may be managed, but not that some
traits are unresolvable.

Option 2 precludes the ability to differentiate between unmanaged trait
sets and unresolvable component traits and so is not a viable option.

## Further notes

The chosen option effectively formalises the meaning of related API
methods as follows:

### `managementPolicy`

For each Trait Set supplied by the Host (defining a concrete Entity type
specialisation), the Manager will return a `TraitsData` instance imbued
with:

- Domain-specific policy traits that describe the Manager's handling of
  entities with that trait set.
- Any traits from the query set that have properties whose data can be
  resolved by (read context) or registered with (write context) the
  Manager when the supplied Entity Reference points to an entity of that
  trait set.

> Note:
> Traits in the queried trait set with no properties will never be imbued
> in the result. This significantly simplifies implementation in the
> manager as it only needs to handle traits that it knows how to process
> property values for. If a host wishes to determine if any given entity
> has a particular trait, the ([forthcoming](https://github.com/OpenAssetIO/OpenAssetIO/issues/31))
> `entityTraits` method should be used.

### `entityTraits`

For each Entity Reference supplied by the Host, the Manager will return
a TraitSet containing the IDs of all traits possessed by that entity
that define its type.

This will include all traits required to correctly type that entity,
regardless of whether the Manager is capable of providing data for all
of those traits. I.e the Trait Set the entity was registered with if
created through the API.

E.g. in the above scenario, the Manager would be expected to return `{
'file', 'image', 'colorMangaed' }` (i.e. those of the
`ImageSpecification`) for any images, even though it will only ever
resolve/register `file` trait data.

This is the differentiator between `entityTraits` and
`managementPolicy` - this queries the type of a specific entity, the
other its data policy for a specific type of entity.

### `resolve`

For each Entity Reference and the Trait Set supplied by the host, the
Manager will return a `TraitsData` instance imbued with:

- Any trait with associated property values that is understood by
  the Manager that the Entity has data for (including null values).

> Note:
> This means the traits imbued in the result should match (or be a
> subset of) the intersection of the requested trait set and those
> imbued in the `managementPolicy` response when queried with the
> entity's trait set. I.e, no traits here that weren't in the policy
> response.

As only data-holding traits will potentially be imbued, this means
`resolve` should not be used to determine if an entity has a particular
trait. Use `entityTraits` for this task instead.

### `preflight`

For each Entity Reference and the Trait Set supplied by the Host, the
Manager will:

- Error if a required Trait is missing from the supplied trait set (i.e.
  it is missing data required to fully define the resulting entity).

### `register`

For each Entity Reference and `TraitsData` supplied by the Host, the
manager will persist:

- The complete Trait Set (i.e. trait ids) to form the typing information.
- The values for the properties of any traits in the set that it
  reported as being supported in response to a write context
  `managementPolicy` query for the supplied data's Trait Set.

> Note:
> Some further discussion is needed as to whether persisted trait sets
> should be searchable at a later date using only a sub-set of their
> trait Ids. E.g, if searching for `{'file', 'image'}`, should return
> all Entities with those traits as a sub-set of their traits, vs only
> those with that exact set. This may have a significant impact on
> back-end database implementations depending on their existing
> approach.
