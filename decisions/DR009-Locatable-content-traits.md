# DR009 Locatable content traits

-   **Status:** Decided
-   **Impact:** High
-   **Driver:** @foundrytom
-   **Approver:** @feltech
-   **Contributors:** @mmazerole @feltech @carmenpinto
-   **Outcome:** We will use an URL-only approach, until there is
    sufficient practical usage to warrant any other more complex
    strategy.

## Background

A specification composes one or more traits. A trait has zero or more
properties that hold simple-typed values. When an entity (asset) is
resolved through OpenAssetIO, the manager populates a specification
instance with the any of the requested traits (and their properties)
that are applicable to the referenced entity.

When a specification holding multiple traits is used as a classifier,
the traits are considered additive and specialize the type of entity
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
being more future proof, as nearly all[^1] file paths can be written as
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
on the process environment. It is critical however, that rewriting the
response should not change the interpretation of the data, i.e. its
format.

A manager may take care of re-locating data, and may be able to make the
same entity data available via multiple means (eg: file on disk, http
stream etc.).

Traits are by design, atomic, in that adding a trait to an entity should
not affect the data represented by an existing trait.

## Options considered

### Option 1

An additional property-less `file` trait that when composed with a
`locatableContent` trait holding an URL specializes the specification
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
-   Requires a manager to potentially re-write data depending on the
    exact traits used for registration and resolution, converting
    between paths/URLs.

### Option 2

A distinct `fileLocatableContent` trait that holds a `path`, used in
place of the URL-holding `locatableContent` when filesystem-only access
is required.

#### Pros

-   Explicitly determines when a host requires data to be available
    through the file system.
-   More explicit representation of the filtering required during
    browsing/etc.
-   No string manipulation overhead in path-based hosts.

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
`locatableContentReader` trait in the caller Context's locale.

#### Pros

-   Allows the host to declare the locator strategies it supports to
    access content (eg: `path`, `URL`, etc.), which can influence
    `resolve` and browsing.
-   No string manipulation overhead in path-based hosts.
-   No need for duplicate specifications.

#### Cons

-   The interpretation of the `location` property is not constant.
    This prohibits the generic store/recall of trait properties which
    violates a core API tenet. It is valid for a manager to rewrite
    property values as appropriate, but their interpretation should
    not change.
-   The manager must rewrite all resolved values accordingly.
-   It precludes both a path and a URL from being returned.

### Option 4

A single `locatableContent` trait that holds a `location` property,
whose content is determined by an accompanying `locationFormat`
property.

An additional local could be set to hint to the manager the preferred
format for the location, but it is not required.

#### Pros

-   Trait data is atomic with constant interpretation.
-   Reduces string manipulation overhead when the format is aligned
    with the host and manager.
-   Avoids any specification duplication.
-   Locale hinting provides an opt-in runtime optimization
    opportunity.

#### Cons

-   Significantly increases the code complexity and overhead on the
    host side as all potential formats need to be handled.

### Option 5

A single `locatableContent` trait that holds a `location` property with
an URL to the data.

#### Pros

-   Entirely stable.
-   Using a constant value interpretation that facilitates generic
    handling of the value.
-   Avoids any specification duplication.

#### Cons

-   String manipulation overhead, including encoding/decoding of
    special characters including those used for frame tokens.
-   UNC path handling needs careful consideration[^1].

## Outcome

The OpenAssetIO-MediaCreation specification library will adopt the
URL-only approach. All other options introduce either additional
complexity or violate core API design principals.

This option is the simplest and most consistent. It can be converted to
several of the other options at a later date if required, once more
practical applications of the API have been explored, and the
performance considerations of the additional string manipulation
properly measured and understood.

[^1]: See [this saga](https://bugzilla.mozilla.org/show_bug.cgi?id=66194).
