# DR024 Manager capability introspection

- **Status:** Decided
- **Driver:** @foundrytom
- **Contributors:** Assorted (2010-2012).
- **Outcome:** OpenAssetIO will support manager behaviour introspection
  using a `managementPolicy` method parameterized by trait set and
  access.

> **Note:**
> This DR was added retrospectively - to capture choices made prior to
> the decision record mechanism being adopted (circa 2012). As such, it
> is not in chronological order in relation to the other records.

## Background

A fundamental design constraint of OpenAssetIO is that neither the host
or manager should need to rely on the particular identity of the other
in order to function. However, as each implementation may not support
all API features, a mechanism is required to allow the Host (as
initiator of the API and communications) to determine what functionality
is provided by any given Manager, without knowing its specific identity.
This information is usually used for:

- Adaptation of UX to enable/disable/control entity related workflows to
  avoid errors or presentation of unsupported functionality.
- Manage the run-time cost of asset management via the API.

## Relevant data

The need for introspection was driven by numerous scenarios encountered
during the adoption of OpenAssetIO's "predecessor" - the Katana Asset
API, and more broadly, whilst building prototype workflows to support a
breadth of editorial and post-production data exchanges. Two
representative scenarios are illustrated below.

### Managing user experience in an editorial workflow

A non-linear timeline based video editing application wished to provide
functionality for ingesting new and updated material into a production
pipeline. This included changes to timeline clips and their duration,
and management of their underlying media.

The rough business logic is as follows:

1. In a clean timeline, an EDL (Edit Decision List) is imported into the
   application from a file-based source (no entity references are known
   at this point). This creates clips on a timeline and references to
   the underlying media.

2. If the configured manager supports the publishing of "Shots",
   then controls are added to allow timeline tracks/clips to be used to
   publish a Shot list to the Manager.

3. If the configured manager supports the ability to store frame-range
   information with these shots, controls are added to publish shot
   timings from the timeline clips.

4. If the configured manager supports the publishing of "Image
   Sequences", then controls are added to allow the media used in the
   timeline to be published and version managed via the Manager.

5. If the configured manager supports the querying of appropriate
   relationships, and entity "types", the controls are added to allow
   the Synchronization of the timeline clips and media with existing
   manager.

Note that at this point, there is no existing entity information within
the application, and so the host needs to be able to introspect
capabilities of the manager without an existing entity reference.

Depending on supported features, the approximate control flow for a full
synchronization process is:

1. Ask the user to supply an anchor entity reference (e.g.: via
   delegated browsing), that is considered the 'parent' for the shots to
   be managed.

2. Query shots related to the supplied reference, and compare with
   timeline clips.

3. If Image Sequences are managed, query related sequences for each
   matched shot.

4. If frame range management is supported, query frame ranges for each
   matching shot and image sequence.

5. Compare shot list, media and timing information, present the user
   with a suitable diff-view, with controls for which actions to perform
   (create/delete missing shots, set/update frame ranges, create/update
   image sequences and their timings).

In order for the user to understand what is possible, and not attempt
actions that will errors due to lack of support from the Manager, the
Host needs to introspect the Managers capabilities and only present UX
that is relevant to those capabilities.

### Managing runtime overhead in scene expansion

A scene management application that uses a deferred node graph to
perform scene aggregation, processing and real-time manipulation of 3D
data and its translation to a rendering engine, needs to optimize
performance in all cases to ensure maximum performance. Either to aim
for real-time user feedback, or minimize core hours in massively
distributed workflows.

During integration of Katana into several studio pipelines, it was
noted that the degree of "assetization" each pipeline adopted varied
greatly.
Katana's assumption that "everything was managed" lead to significant
runtime overhead.

Of particular note was the facility to allow asset management of
Shader parameters. The requirement here was that a pipeline may wish to
assetize shader parameters (e.g.: textures). As a consequence, the scene
build process is required to consider each string shader parameter as a
potential entity reference. In typical production scenes this can result
in hundreds of thousands of parameters needing consideration.

Requests were made by pipeline owners to allow them to "turn off"
assetization within different parts of the application where they did
not need it. The shader case in particular caused specific problems due
to its high call volume, and the desire for some asset management
systems to be written in Python, which results in thread synchronization
overhead and a higher per-call cost.

Redundant entry into Asset API code usually manifested itself as UI
stalls, negative impact on real-time scene updates such as during
interactive lighting renders, or higher time-to-first-pixel numbers in
general.

## Options considered

### Option 1 - An entity reference based introspection mechanism

Add an introspection mechanism that allows a Host to query the Manager
for its capabilities regarding specific entity references. This
mechanism could then be queried in relation to specific entities
interacted with by the user.

#### Pros

- Capabilities can vary from entity to entity, allowing introspection to
  accurately reflect what capabilities or data may be supported for any
  given entity. This may vary based on the history or current state of
  the entity.

#### Cons

- Requires an entity reference to be known to query capability - but
  references would inherently be unavailable for any entity with an
  unsupported trait set.

- Capabilities can vary from entity-to-entity, which makes batching and
  other API operations significantly more complex, and may require
  additional per-entity API calls to ensure correct behavior of the
  host.

- Querying capabilities relating to relationships is harder to
  incorporate without a more complex signature as they always required a
  trait set to be defined to describe the 'edge'.

### Option 2 - A trait set based introspection mechanism

Add an introspection mechanism that allows a Host to query the Manager
for its capabilities regarding specific "types" of entities or
relationships. The "type" is determined by its trait set.

#### Pros

- Capabilities can not vary per entity or relationship type. Allowing
  high-level optimizations or UX adaptation to be performed.

- Does not require an entity reference, allowing unsupported
  capabilities to be determined in advance of any interactions/errors,
  further extending the possibility for optimization.

- Relationship queries are also defined by trait sets and so fit
  naturally into the calling pattern.

#### Cons

- Capabilities can not vary per entity, which may result in unexpected
   failures if a specific manager was not also consistent for any given
   trait set.

- Requires an additional mechanism to determine any entity-specific
  capabilities that may occur, increasing API complexity.

## Outcome

OpenAssetIO will adopt a trait-set parameterized high-level Manager
capability introspection mechanism, and any subsequent requirements for
entity-specific introspection will be provided through other means.

This mechanism will allow the manager to define what capabilities it
supports for any given trait set, and for which of those traits the
manager is notionally capable of storing or recalling data.

As a result, we are defining that manager capabilities are considered
invariant for entities with the same trait set, and consequently, also
invariant at runtime.

This is to allow applications to ensure end-user workflows are
representative of what is possible with the configured manager, and
optimize their implementations to avoid unnecessary interactions for
unsupported entity types.

The method will also be parameterized by 'access' (read/write et al).
There are enough differences between read and write workflows, and the
level of support provided by any given manager. Some managers may be
read-only libraries, or their implementations may be undergoing phased
development based on demand.

### Rationale

The requirement to determine what is unsupported is just as important as
what is supported. Any mechanism that requires an entity reference to
function is unsuitable for this task, as entity references are simply
not known at the time capabilities must be determined in many real-world
use cases (see the relevant data section). They are also inherently
never available for an unsupported entity trait set.

The entity reference could be made optional in the reference-based
approach, but it would then require the addition of a trait set to
stand-in for a "generic" entity of that type. This would help as a
trait set would then also allow a relationship to be queried. It was
felt that the fact though that this method would then have two (or even
three) distinct and parameterizations was a strong indication it should
be two separate mechanisms for clarity of purpose as the interaction
between the two optional arguments would be harder to define clearly.

The introduction of per-entity capability variation also introduces a
significant complexity in the design and implementation of host code
that deals with a sequence of interactions between multiple entities
(see the editorial example above). Not only does it increase code path
complexity, as it _requires_ a per-entity check for each discreet input.
This precludes certain assumptions that allow data to be more easily
aggregated into a batched query - requiring request specific re-batching
to be performed.

This also extends to publishing where host-provided vs manager-provided
data at an entity-specific level adds a level of complexity that has not
yet been seen to be required in observed pipelines.

When capabilities and supported data are defined as constant for any
given trait set it allows adaptation at a much higher level, and
significantly simplifies implementation.

Defining that capabilities are tied to a trait set, not a specific
entity is not without its downsides, but it aligns well with
available implementations, and a broader analysis of known asset
management systems. It should be noted that such a mechanism does not
guarantee that data is available for all entities (the design of
`resolve` is a soft failure), it simply informs the Host that any given
Manager at least declares support of that data at an implementation
level. Making this trade-off feel a reasonable compromise given the
benefits of up-front knowledge, and complexity reduction.

If precise, advanced entity-specific introspection is needed for
particular workflows (for example, determining the trait set of a pasted
entity reference), it is felt that this would be better suited to a more
tailored mechanism that makes it clear its results _are_ entity specific
(e.g. `entityTraits`).

In the cases of reactionary data handling/performance (see the shader
parameter example), the question of whether the advent of optimizations
such as `constants.kInfoKey_EntityReferencesMatchPrefix` make this a
non-issue. Unfortunately not all Managers have the ability to support an
optimized constant reference prefix. File-path remapping managers may not
have any such uniform string that can be used to short-circuit API
evaluation. It is also possible to write these Managers in Python or
some other non-performant language. As such the `isEntityReference`
check must be presumed to be non-trivial in at least some situations.

There are without doubt some compromises and constraints in the decided
approach, but it seems the best balance of complexity reduction and the
facilitation of the coherent end-user workflows required by Host
integrations based on known system architectures at the time.
