# DR017 Entity version queries

- **Status:** Decided
- **Impact:** High
- **Driver:** @foundrytom @feltech
- **Approver:** @elliotcmorris @feltech @mattdaw @antirotor
- **Contributors:** @foundrytom @feltech @elliotcmorris
- **Outcome:** The Version APIs will be moved to MediaCreation.

## Background

The majority of asset management systems integrated with OpenAssetIO
provide some kind of versioning mechanism for the entities they manage.

A simple example of such takes the form that where any specific logical
entity may change over time, each change creates a new immutable version
of that entity. The connectivity of the entity in the asset graph
generally remains unchanged. In such a situation, if the graph is
visualized in two dimensions, one may think of versions as occupying the
third dimension, into the page.

There are countless variations on this approach, and it is critical that
OpenAssetIO itself has no specific interest in determining how
versioning should work, or how versions should be addressed within the
system. This is left entirely up to the implementation of any specific
manager. There are a couple of intersections however, when:

- New data is created.
- A host needs to present entity version information to a user.
- A host needs to allow the user to change the version of
  an entity that is loaded.

For the purposes of this document we will ignore the data creation
scenario. This is well-defined in the API (when data is published, the
manager is free to determine if this is a mutation, new version or new
entity - by considering the target reference and trait set of the
provided data).

We shall instead focus on the matters of determining version information
for existing entities, in order to determine whether there is a
justifiable place for first-class version query methods with the core
API.

## Relevant data

### The existing API

The existing API is based on a long-term fork of the Katana Asset API,
which was subsequently generalized and extended through practical
development of editorial workflows.

It comprises the following methods (illustrated in singular form for
clarity):

| Method                        | Data                  | Notes                  |
| ----------------------------- | --------------------- | ---------------------- |
| `entityVersion(ref)`          | `str`                 | Current entity version |
| `entityVersions(ref)`         | `[(str, EntityRef),]` | All versions           |
| `finalizedEntityVersion(ref)` | `EntityRef`           | Frozen entity version  |

These were used in production to:

- Provide a presentation of the current version of an entity to users.
- Allow users to pick alternate versions for use.
- Obtain stable references for persistence.

###  The evolution of the entity data model

As described in
[DR007](./DR007-Hierarchical-or-compositional-traits-for-specifications.md)
and [DR008](./DR008-Unify-the-entity-data-model.md), the OpenAssetIO
data model has evolved significantly since these methods were
introduced.

Critically, traits facilitate structured data groupings that can be
resolved independently for any given entity.

When the current version query methods were added, the API surface area
was far more explicit. It formally defined specific well-known fields
for popular production themes. This created a clear, but rigid API, that
struggled to tread the line between being opinionated, and allowing
enough flexibility for modern pipelines.

Recently, the API has changed its approach slightly. We now de-couple
the core data transport layer (`openassetio`) from its industry-specific
applications (eg. `openassetio-mediacreation`). This hopefully allows
sector-sepcfic flexibility, whilst retaining a solid well-defined
surface are.

The new trait-based resolution framework allows a Host to query
additional structured data by passing extra traits to `resolve`
avoiding the need for additional API calls.

It was noted during this transition, that the current versions API is
entirely expressible through these existing API methods, raising the question of
"why do we need to treat versions any differently to other
relationships"?

###  Decomposing the current methods

The existing methods can be decomposed into one or more of the base API
methods in conjunction with a new `Version` trait:

| Existing Method          | Alternative                       |
| ------------------------ | --------------------------------- |
| `entityVersion`          | `resolve`                         |
| `entityVersions`         | `getWithRelationship` + `resolve` |
| `finalizedEntityVersion` | `getWithRelationship`             |

###  Call count impact

Previously, specific methods have been justified as facilitating
manager optimizations for the specific data needed. A quick glance at
the alternative for `entityVersions` suggests that we would be
increasing server load by devolving back to the generic queries.

Let put this to the test in practical scenarios:

#### Displaying a version picker menu

A DCC may wish to provide a version picker to allow a user to switch out
the active version of a entity. Depending on how much information needs
to be shown, there is potentially a missed optimisation in the
degenerate formulation:

| Presentation     | Existing                   | Decomposed                      | Difference |
| ------------     | --------                   | ----------                      | ---------- |
| Version          | `entityVersions`           | `getWithRelationship + resolve` | +1         |
| Version and Date | `entityVersions + resolve` | `getWithRelationship + resolve` | 0          |

#### Annotating a timeline with clip name and version info

An editorial tool needs to decorate the display of potentially thousands
of clips on a timeline, so they can be identified by the user. In this
situation, separate methods for versioning predicates an additional API
call when this information is needed as it can't be obtained through
`resolve` with the other entity data.

| Presentation     | Existing                    | Decomposed | Difference |
| ---------------- | --------------------------- | ---------- | ---------- |
| Name             | `resolve`                   | `resolve`  | 0          |
| Name and Version | `resolve` + `entityVersion` | `resolve`  | -1         |

#### Checking for newer versions of an entity

If a tool wishes to indicate to a user that a new version is available
for a specific entity, with UI feedback.

| Presentation     | Existing                    | Decomposed                        | Difference |
| ---------------- | --------------------------- | --------------------------------- | ---------- |
| Existence only   | `entityVersions`            | `getWithRelationship`             | 0          |
| Version          | `entityVersions`            | `getWithRelationship` + `resolve` | +1         |
| Version and Date | `entityVersion` + `resolve` | `getWithRelationship` + `resolve` | 0          |

#### Asset export

Traversing the history of an asset, for use in some other detached
scenario, that includes all trait data.

| Existing                     | Decomposed                        | Difference |
| ---------------------------- | --------------------------------- | ---------- |
| `entityVersions` + `resolve` | `getWithRelationship` + `resolve` | 0          |

#### Summary

| Scenario                  | Existing | Decomposed | Cost | Call Volume |
| ------------------------- | -------- | ---------- | ---- | ----------- |
| Basic Picker              | 1        | 2          | +1   | Low         |
| Extended Picker           | 2        | 2          | 0    | Low         |
| Clip Annotation           | 1        | 1          | 0    | Med         |
| Clip Versioned Annotation | 2        | 1          | -1   | Med         |
| Export                    | 2        | 2          | 0    | Low         |
| Updated check             | 1        | 1          | 0    | Low/Med     |
| Updated check w/version   | 1        | 2          | +1   | Low/Med     |
| Updated check w/info      | 2        | 2          | 0    | Low/Med     |

## Options considered

### Option 1 - Keep first-class versions API

With this option, OpenAssetIO would maintain first-class methods to
introspect entity versions.

#### Pros

- Optimal in situations where the version name is the only required
  information to be presented to the user. OpenAssetIO axioms suggest
  that more sophisticated presentations should be done through UI
  delegation rather than first-class understanding of agreed common
  themes.
- Can enforce the use of paged API methods.
- Formalizes the definition of a version in the core API. Without this
  the API tends towards nothing more than a generic database SDK. Its
  presence reminds the manager that versioning must be considered.

#### Cons

- Formalizes the definition of a version in the core API, contrary to
  (other) OpenAssetIO axioms. Extensions to version information (eg:
  additional metadata) require a core update and precludes
  domain-specific versioning models. Retrieved data is fixed at compile
  time based on library version.
- Increases API requests when information other than the name is also
  required as the specific methods are the only way to retrieve that
  information.
- Larger API surface area to maintain and duplicate edge case business
  logic in manager implementations increases chances of programming
  errors.
- In many real-world managers, not all entities are versioned, a
  first-class method may suggest that the API requires them to be (it
  doesn't).

### Option 2 - Decompose to basic API methods

With this option, all versioning information would be queried through
the generic `resolve`, `getWithRelationship` API methods.

#### Pros

- Facilitates domain-specific versioning models through alternate
  traits, without a core API change. OpenAssetIO axioms dictate that the
  core API should not have strong opinions about domain specific
  concepts.
- Allows arbitrary data to be queried alongside versioning information
  (by expanding the resolved trait set), facilitating runtime
  customization of the user presentation with constant call count.
- Smaller API surface area to maintain across language bindings/test
  infrastructure, and fewer methods for a manager to implement, reducing
  edge-case handling programming errors.
- Host conveniences can be provided in domain-specific layers that mimic
  core API methods, discouraging misuse.
- Better reflects that versioning is not a requirement of the API
  itself, which is important as not all entities are versioned in any
  given manager.

#### Cons

- More abstract - manager's need to remember to add yet another switch
  case to an already generic API method, versioning may be overlooked.
- Increases API requests when only the version name is required.
- Precludes any version-specific behaviour/failure modes.
- Hosts may inadvertently use non-paged API methods resulting in runtime
  stalls and poor UX.

## Outcome

OpenAssetIO will remove specific APIs for version information retrieval
from the core API, and migrate the functionality to new Traits,
Specifications and/or convenience methods in OpenAssetIO-MediaCreation.

### Rationale

We now have more flexible data query mechanisms within the core API, and
there is no expectation that versioning is supported by every entity.

We made a similar move when we removed the concept of a 'primary string'
(usually a path) from earlier iterations.

OpenAssetIO is an industry agnostic abstraction layer. Consensus amongst
the community, and similar projects (eg. the MovieLabs
[Ontology](https://movielabs.com/production-technology/ontology-for-media-creation/))
is that abstraction layers should not be overly opinionated about the
nature of versions. This is a pipeline-domain concern.

In many real-world scenarios for example, versioning is inherently
linked with concepts such as departments and approval status.

As such, OpenAssetIO-MediaCreation - the Media and Entertainment
specialisation of OpenAssetIO - is the correct place to defined what
versioning means in that domain, and it's associated semantics.

Overall performance is similar for both options. We feel that the
additional API call required in the very specific situation of wanting
to know the version _name_ only, is offset by the likely more
common situation of wanting to present current versioning information
alongside data from other traits.

We also feel that the additional benefits of a smaller core API surface
area outweigh the marginal growth in complexity of the implementation of
the remaining methods.
