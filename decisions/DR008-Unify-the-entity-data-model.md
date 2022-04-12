# DR008 Unify the entity data model

-   **Status:** Decided
-   **Impact:** High
-   **Driver:** @foundrytom
-   **Approver:** @carmenpinto @feltech
-   **Outcome:** The existing `getEntityAttributes` and
    `resolveEntityReference` methods will be combined into a trait-centric
    resolution mechanism.

## Background

When a host application (DCC tool, pipeline script, etc.) wishes to
retrieve data from one of a manager's entities (assets), it has two
options:

1. The "primary string" can be resolved.
2. Arbitrary key-value pairs of "attributes" can be queried.

The primary string is thought of as "the string the host would have
had if there were no asset management system", and attributes are
"bonus data that may be useful".

The reason for this is the origins of the API. It is based on the Katana
Asset API, where it is predominantly used to resolve strings, the
majority of which being file paths.

OpenAssetIO was forked to solve a wider variety of workflows, including
editorial processes. This broadened the scope of what kinds of entity
needed to be handled by the API, and consequently necessitated the
ability to store and recall more than just single strings.

If we consider a "shot" (a series of frames covered by a single camera
angle in a film or tv show), the concept of a primary string is somewhat
meaningless. A shot may have a name _and_ a frame range, where the frame
range is actually the most important part.

To provide a working solution to this problem, OpenAssetIO gained the
attributes mechanism as it stands today, and the specification
classification hierarchy to help everyone work out what "kind of thing"
any given entity was.

Upon this, a somewhat fragile scaffolding of conventions grew. It was
expected that certain specifications (or an element of their parent
hierarchy) had certain attributes, and perhaps more comically, that for
some specifications of entity, the primary string was "largely
irrelevant".

In short, the hard partitioning between the primary string and
attributes, established at the APIs origin was becoming less suited to
the breadth of scenarios encountered today. The hierarchical
specifications mechanism was a reaction to this, but one that in itself
was inherently flawed.

The the recent switch of the specifications mechanism from a
hierarchical taxonomy to one that composes several distinct traits (see
[DR007](DR007-Hierarchical-or-compositional-traits-for-specifications.md))
resolves a key weakness of the previous design. It is now possible to
concretely and unambiguously define a specific entity trait and what
data should be associated with it.

This removes the need for the hard partitioning of a "primary string"
and attributes at the API level, and allows OpenAssetIO to de-couple
itself from the nature of any particular kind of entity.

It hopefully ensures that the API remains unambiguous and has more of a
chance to remain fit for purpose into the future, as modern pipelines
diverge from traditional file-centric workflows.

## Relevant data

-   Within the scenarios in which OpenAssetIO will be employed, there is
    probably no single dominant type of entity when counting by number
    of unique workflows. However, in most current pipelines there is
    certainly a dominance of URI -> file path transformations when
    counted by number of invocations.

-   Integration of OpenAssetIO into a host application or tool provides
    most value when it is used beyond the simple resolution of URIs to
    paths. For example, a render node generating images using the API
    not only to determine where to put the images, but what colorspace,
    file format, bit depth and compression settings to use

-   A primary design goal for OpenAssetIO is clarity. There should be as
    little ambiguity as to its usage or the expected behavior of a host
    or manager as possible.

-   The current API as implemented suggests that the lifetime of
    attributes and the primary string are different. The primary string
    can only be set during `register`, whereas attributes can be
    updated. This behavior is incorrect and the work
    [here](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/4)
    will address this inconsistency. For the sake of this decision, the
    lifetimes of both data elements can be considered the same.

-   [#247](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/247),
    and the appendix below contain further details of the proposed
    approach.

## Options considered

### Option 1

Keep the status quo. Retain the existing concepts and separation of the
"primary string" and "attributes" mechanisms.

#### Pros

-   The concept of simple string-string resolution is well understood
    across the industry.
-   Provides a fast-path for the case of string-string transformations
    as only that specific string is required to be retrieved from
    storage.
-   Facilitates generic resolution without any understanding of the
    nature or intended use of the the value.

#### Cons

-   The meaning of the "primary string" is highly ambiguous for all
    involved.
-   Many entities have no conceptual "primary string".
-   Hosts requiring the primary string _and_ attributes must make two
    API calls, increasing query latency.
-   Hosts must request arbitrary attributes by name, with no specific
    mechanism to create common definitions or collections of these.
-   The API is hard-coded with the semantics of one particular category
    of entity (one with a primary string), which burdens future
    applications.
-   The query API is asymmetrical to the publishing API.
-   Runtime/compile time validation of data schemas for responses is
    much harder for the manager or host as attributes are only loosely
    coupled to any concrete API.

Estimated cost: None

### Option 2

Unify entity data into a trait-centric mechanism.

This would replace `resolveEntityReference` and `getEntityAttributes`
with a singular `resolve` method that takes one or more traits.

The result of resolution provides any available entity data for each of
the specified trait's properties.

#### Pros

-   Using traits as a descriptor means the API expresses entity data
    schemas in a first-class, introspectable way.
-   The intended use of resolved data is always clearly communicated
    from the host to the manager through the requested traits.
-   The API is de-coupled from the specifics of any entity's data
    schema.
-   Queries are always a singular API call regardless of the number of
    data fields required.
-   The registration and query APIs are symmetrical.
-   The trait/specification view APIs can be used to ensure
    runtime/compile time correctness of data responses and access by
    both managers and hosts.

#### Cons

-   The single string-string path of the primary string has no direct
    mapping:
    -   At a programming level, this may have an overhead in terms of
        allocations etc...
    -   The concept of a "generic" resolution is harder as the host must
        always request a specific trait. This could be remedied by
        introducing a generic trait (eg. a "string trait"), but this
        undoes some of the benefits of specificity.
-   Effort required to updated documentation, example code, onboarding
    material etc.

Estimated cost: Medium

## Outcome

The API will move to the trait-centric unified entity data model and
resolution mechanism.

## Rationale

The clarity of concrete schema definitions through traits, and the
de-coupling of API from the specifics of any particular kind of entity
will provide benefits to the long term usability and stability of the
project.

We believe these benefits outweigh the specific case of generic
resolution expressed through a first-class API call, as this can be
recreated with a suitably generic `string` trait if specifically
required.

In addition, for a significant number of projected use cases, multiple
API calls (to resolve then attributes) are needed anyway. The combined
proposal provides for more optimization opportunities for these cases
than the existing API.

The resulting demands made on the manager's implementation are
approximately the same in either case as there are always entities that
were authored outside of OpenAssetIO interactions, that would require
work to determine what a suitable primary string (or string trait value)
should be.

We believe that in real-world scenarios, any overhead the data
structures required to support the trait-based return types would be
relatively insignificant compared to all other work performed by a
manager to satisfy any given lookup.

### Performance measurements

A valid concern regarding this change is that it precludes a happy-path
optimization were a single string of a single trait is required for
resolution, and the overhead of a view-based API would be significant.

The following timings were obtained using a naive, un-optimized C++
implementation of the [generic resolution](#generic-resolution) sketch
in the appendix below. In the implementation, the manager is in the
ideal situation where results are cached in-process in a pre-populated
`std::unordered_map`:

```
Queries: 100000
Batch size: 1
Wall-clock time (Total):
  resolveEntityReference: 43 ms
  resolve: 124 ms
Wall-clock time (Per-call):
  resolveEntityReference: 0.00043ms
  resolve: 0.00124ms
```

We believe that in typical real-world scenarios, adding less than tenth
of a second onto the time to resolve a _hundred thousand_ entities is
not a significant concern compared to the rest of work-to-be-done by the
system to satisfy those queries, or make use of the resulting data.

## Appendix

What follows in a comparative illustration of the two approaches, the
code for Option 1 assumes that the work has been done to make attributes
versionable and consistent with
[#4](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/4),
and that the relevant API methods have been updated to work with trait
sets.

### Preamble

The examples assume the following traits and specifications are
available - allowing a file-based image to be described:

```cpp
trait BlobTrait {
    name: "blob",
    props: { url: str, mimeType: str }
}

trait ImageTrait {
    name: "image",
    props: { colorSpace: str }
}

spec ImageSpec {
    traits: ["blob", "image"]
}
```

### Publishing an image

This example illustrates a host wanting to publish an image with its
associated color space, to ensure it is accurately tracked.

```python
img = ImageSpec()
img.blobTrait().setUrl("file:///some/render.exr")
img.imageTrait().setColorSpace("ACES - ACES2065-1")
```

#### Option 1

```python
manager.register(
    "file:///some/render.exr", img.toAttributes(),
    img.traitNames, target_ref, context)
```

This is ambiguous, as should the blob trait properties be included in
`toAttributes`? The `url` is the primary string, but `mimeType` needs
to go via attributes (if it was set).

#### Option 2

```python
manager.register(img, target_ref, context)
```

Removes the ambiguity as the spec, complete with its data for all
applicable traits is registered in one go, with no duplication or need
to work out 'which single property' becomes the primary string.

### Resolving data for an image

This example shows a host wanting to read an image with the correct
color space.

#### Option 1

```python
path = manager.resolveEntityReference(img_ref, context)
attr = manager.getEntityAttributes(img_ref, ImageTrait.attrNames, context)

color_space = ImageTrait(attr).getColorSpace()
```

Note the asymmetry to `register`, only the `ImageTrait` is needed for
lookup as otherwise if `ImageSpecification` was used, it would also
request the already accessed `url` from the blob, which we "know" we
already have through the primary string. Maybe we should have omitted
resolve and just fetched it all via attributes?

#### Option 2

```python
data = manager.resolve(img_ref, ImageSpec.traitNames, context)

img = ImageSpec(data)
path = img.blobTrait().getUrl()
color_space = img.imageTrait().getColorSpace()
```

The host simply requests exactly which data it needs in a single call,
and the requirement to reason whether the primary string was meaningful
or not evaporates.

### Generic resolution

Some generic code wishes to 'resolve' an entity to its primary string
without any understanding of its specific usage as simple wrapper around
any generic string parameter.

#### Option 1

The manager is already expected to figure out what to return as a
primary string based type of entity it is within its domain (or, what
was registered if the entity was created through OpenAssetIO).

```python
str_value = manager.resolveEntityReference(some_ref, context)
```

#### Option 2

In order to support a similar functionality, the trait approach would
have to define a generic `StringTrait` with a `value` property to
instruct the manager to perform the same guessed conversion as before
for existing entities, or ones registered through OpenAssetIO without
the `string` trait.

```python
data = manager.resolve(some_ref, [StringTrait.name], context)
str_value = StringTrait(data).getValue(default='')
```
