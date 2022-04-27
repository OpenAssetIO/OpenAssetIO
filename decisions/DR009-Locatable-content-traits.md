# DR009 Locatable content traits

-   **Status:** Decided
-   **Impact:** High
-   **Driver:** @foundrytom
-   **Approver:** @feltech
-   **Contributors:** @mmazerole @feltech
-   **Outcome:** Entities that hold data elsewhere, locatable by a URL
    will use a single `locatableContent` trait, regardless of how this
    data is accessed.

## Background

A specification composes one or more traits. A trait has zero or more
properties that hold simple-typed values. When an entity (asset) is
resolved through OpenAssetIO, the manager populates a specification
instance with the any of the requested traits (and their properties)
that are applicable to the referenced entity.

When a specification holding multiple traits is used as a classifier,
the traits are considered additive and specialize the type entity
referenced. For example, a specification with `traitA` and `traitB`
means that the entity should have both `traitA` and `traitB`.

When a host wishes to consume entity data that is not in-lined in a
trait property value, this is usually done via a side-car resource.
Historically, this has been through a file on disk. Moving forward, the
file-centric approach is outmoded and there is strong interest in moving
to a URL+scheme based behavior across the industry.

We need to standardize the trait(s) used when composing a specification
that describes entities with data that is not returned in-line as part
of the `resolve` call, and how this data is located.

## Relevant data

Using a trait holding an URL instead of a file path has been proposed as
being more future proof, as all[^1] file paths can be written as
`file://` scheme URLs.

At the time of writing, the majority of hosts are restricted to
file-based access for entity data. The overhead of adding and then
stripping the `file://` prefix either side of a `resolve` call is
potentially wasteful in high call volume scenarios.

A merit of the trait system is that one of several traits could be
selected to resolve an entity in the most appropriate way based on the
capabilities of the host.

When a host makes an API query to a manager, the locale supplied in the
context object is the mechanism that classifies calling context, and
could contain information about supported formats/strategies for read
-to allow the manager to customize its response. A consideration of the
calling context is the standard approach for varying API responses based
on the process environment.

A manager may take care of re-locating data, and may be able to make the
same entity data available via multiple means (eg: file on disk, http
stream etc.).

Traits are by design, atomic, in that adding a trait to an entity should
not affect the data represented by an existing trait.

## Options considered

### Option 1

An additional property-less `file` trait that when composed with a
`locatableContent` trait holding an URL specialises the specification
such that only URLs with the `file` scheme should be returned.

#### Pros

-   Can easily be appended to an existing trait set, removing the
    requirement to have duplicate specifications for path or URL access
    to the same entity data.
-   Explicitly determines when a host requires data to be available
    through the file system.
-   More explicit representation of the filtering required during
    browsing/etc.
-   As the trait is additive, it can simply be omitted when URLs are
    supported with no need to re-write data.

#### Cons

-   Introduces side-effects in trait composition, violating the design
    principal that traits should be atomic.
-   String manipulation overhead may be introduced to remove `file://`
    prefix in path-based hosts.

### Option 2

A distinct `fileLocatableContent` trait that holds a `path`, used in
place of the URL-holding `locatableContent` when filesystem-only access
is required.

#### Pros

-   Explicitly determines when a host requires data to be available
    through the file system.
-   More explicit representation of the filtering required during
    browsing/etc.
-   No sting manipulation overhead in path-based hosts.

#### Cons

-   Requires duplicate specifications to be defined for the same entity
    data to be accessed via path or URL, removing much of the benefits
    gained from traits vs hierarchical specifications.
-   Requires a manager to potentially re-write data depending on the
    exact traits used for registration and resolution, converting
    between paths/URLs.

### Option 3

A single `locatableContent` trait that holds a `location` property,
whose content is determined by the options set in a
`locatableContentReader` trait in the call's Context's locale.

#### Pros

-   Allows the host to declare the locator strategies it supports to
    access content (eg: `path`, `URL`, etc.), which can influence
    `resolve` and browsing.
-   No sting manipulation overhead in path-based hosts.
-   No need for duplicate specifications.
-   Uses the API mechanism for adapting responses at runtime (the
    calling context's locale).

#### Cons

-   The meaning of the `location` property is less well defined, and
    relies on calling context being correctly configured.

## Outcome

The OpenAssetIO-MediaCreation specification library will adopt the
single `locatableContent` trait with a `location` property to describe
entities with external content. The nature of the `location` property's
value will be determined by inspection of the `locatableContentReader`
trait of the calling Context's locale.

## Rationale

Option 3 strikes the best balance of explicit behavior and
flexibility. It makes use of the existing API mechanism for adapting
behavior at runtime, and adheres to trait design principals.

The side-effects of Option 1 - where by the data of the `url` property
of the `locatableContent` trait is affected by the composition of
another trait is illegal, and would significantly complicate the
handling of traits within any manager implementation.

The need to duplicate specifications in Option 2 (and to some extent,
Option 1) negates many of the reasons for using trait composition (over
the old hierarchical approach) to avoid duplication in the first place.

## Appendix

### Sketch

Getting the location of an entity's data, using the traits from
Option 3:

```
trait locatableContent {
	location: str
}

trait locatableContentReader {
    usesURLs: bool = false
    supportedURLSchemes: InfoDictionary
}

specification LocatableContentReaderLocale {
	traits: {"localeContentReader"}
}
```

Defaults to path only resolution:

```python
context = openassetio.Context()
context.locale = LocatableContentReaderLocale()

[entity_data] = manager.resolve([entity_ref], {LocatableContentTrait.kID}, context)

# Default value for usesURLs is False so a path is returned
path = LocatableContentTrait(entity_data).getLocation()  # /path/to/data
```

Enable URL support in the calling context locale and specify supported
schemes:

```python
reader_trait = context.locale.locatableContentReaderTrait()
reader_trait.setUsesURLs(True)
reader_trait.setSupportedURLSchemes({"file": True, "https": True})

[entity_data] = manager.resolve([entity_ref], {LocatableContentTrait.kID}, context)

# The manager now returns a URL instead
url = LocatableContentTrait(entity_data).getLocation()  # https://secure/access/to/data
```


[^1]: Forging UNC paths, for now - see [this saga](https://bugzilla.mozilla.org/show_bug.cgi?id=66194).
