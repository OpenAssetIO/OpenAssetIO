

# DR023 Versioning traits and specifications

- **Status:** To be decided
- **Impact:** High
- **Driver:** @elliotcmorris
- **Approver:** @feltech
- **Contributors:** @elliotcmorris @feltech @reinecke @antirotor
- **Outcome:**  TBC

### Preface
This document refers to the versioning of trait and specification
libraries in general. However, as `openassetio-mediacreation` is the
only one in play at the moment, and since reading "trait and
specifications library" over and over would be tiresome, we will just
use the term `mediacreation` throughout this document.

# Problem Statement
In order to achieve OpenAssetIOs interoperability goal, hosts and
managers must agree on the structure of data exchanged between them.

The `openassetio-mediacreation` defines the agreed standard for interop
objects (called `traits` and `specifications`) across the VFX industry.
Hosts and Managers must agree on the structure of these objects. [These
objects](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation/blob/main/traits.yml)
are currently in a first-pass state, and it's understood that the only
way to come to a solid set of useful shared concepts is via use and
iteration.

OpenAssetIO wants to be thin, and does not want to be "the problem". To
this end, we need a change and versioning process for the traits and
specifications schema which allows maximum compatibility, especially in
the face of the unpredictable version adoption in the VFX industry.

[`openassetio-mediacreation`](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation)
is a generative library, in that it produces trait and specification
view classes representing the objects specified in the source `.yml` via
the `openassetio-traitgen` tool, currently in both the c++ and python
languages. As such, the challenge of versioning is not only descriptive,
but also technical.

# Aims :
- Allow new mediacreation versions to be adopted by managers without
  breaking compatibility with hosts running previous versions.
- Deliver a solid but minimal versioning foundation, that leaves open
  opportunities for implementation conveniences at a later date.
- Allow infinite backwards compatibility for manager implementations.
- Low cognitive load, the OpenAssetIO development ecosystem cannot
  support a complicated/technically intricate solution.
- Minimize burden on manager implementors, whilst keeping in mind the
  prior aims.

# Simplifying assumptions
Versioning is a vast topic, and OpenAssetIO has a lot of moving parts.
For the purposes of not going mad, we will make some tentative
assumptions to simplify discussions.

## Version Format
For illustrative purposes, we will presume flat versioning (v1, v2) etc
for schema versions by default throughout this document. However, we are
considering semver, and may note some semver specific considerations.

## Backwards Compatability Mechanisms

A necessary goal in versioning a schema is to provide mechanisms to be
backwards compatible.

There are a few mechanisms to do this, such as.
- Have the manager bundle all the old versions of `mediacreation` that
  they wish to support in their package
  - A convenient alternative to this would be having
    `openassetio-traitgen` generate all the old versions of the trait
    and specification view types into the library, under a separate
    namespace.
- Provide mechanisms to upgrade and downgrade `mediacreation` types.

Given the effort we have to spend on this, we are going to assume for
the moment that `openassetio-traitgen` generates older versions of trait
types into the library, for use by the manager to perform conversions.
This does not preclude the future addition of automatic
upgrade/downgrade functionality.

For example:
```python
openassetio_mediacreation.legacy.traits.content.LocatableContentTrait_v1
```

## Who adapts
We are going to assume that in most cases, the manager will be
performing trait conversions between versions, with the host defining
the "working version".

Reasons:

- Hosts update less often, and such are more likely to remain on older
  versions of `mediacreation` for longer.
- Managers are likely to be more capable of implementing capable trait
  conversions between versions.
- Hosts "start the conversation", and for some methods that means
  sending a trait or specification along, implying an opinion on
  version. (Although, hosts _could_ query managers for what version of a
  trait they should send via a version aware `managementPolicy` or some
  other mechanism, so this is perhaps a weak argument. That arrangement
  seem intuitively more complex though)
- In many cases, manager plugins are privately owned by pipeline
  authors, who are also in control of when to update the hosts in their
  pipeline.

## Manager/Host Namespace Collisions
With the current state of affairs, a large problem with versioning is
presented when you consider the possibility of namespace collision
between hosts and managers.

For the purpose of this decision, we will assume that two versions of
`mediacreation` can exist in the same process without problematic
namespace collisions, although this remains a problem to be solved.

(Note: Practically, this may mean that we end up strongly recommending
 vendoring mediacreation into manager plugins, especially for python
 libraries which can't do C++ tricks with private symbols.)

## Schema version, package version

The schema version (the version number in the `.yml`) and the package
version (the `openassetio-mediacreation` library version) are separate.

It is possible that updates to `openassetio` or `openassetio-traitgen`
could cause breakages that necessitate a major version update to the
`openassetio-mediacreation` package.

We are assuming that this does **not** imply a schema version update.


# What to Version
In considering how to version the openassetio traits and specifications,
two options immediately present themselves. Version every trait and
specification individually, or version the entire schema as a whole.

## Version every trait
Every trait gets its own disconnected version. This version would have
to travel across the api-boundary along with the trait data. Whilst the obvious
thing would be to enhance the low level `TraitsData` type to have a
first class understanding of versioning, this cannot be so because not
every method takes a `TraitsData` as an argument. The lowest-friction
course of action might be to pack the version into `TraitId`, essentially
doing string-munging to communicate the version across the api-boundary.

Hosts and managers would need to be inspect the version data, which we
could provide conveniences for, and construct the correct version
of the trait view.

```yml
# traits.yml
Camera:
  description: >
    The entity represents a device that captures a view through
    re-projection or encoding into some other form.
  usage:
    - entity
  version: 3
```

```python
# Manager
# In this example, CameraTrait is on version 3
# SpatialTrait is on version 2
#
# The manager is responding to a resolve, needing to populate a
# TraitsData with a camera trait and a spatial trait of the expected
# version
cameraVersion = mediacreation.versionFromTraitId(mediacreation.CameraTrait.kId)
spatialVersion = mediacreation.versionFromTraitId(mediacreation.SpatialTrait.kId)

# Support all known major versions.
# Camera
success_result = TraitsData()
if (cameraVersion >= 3 and cameraVersion < 4):
     trait = mediacreation.CameraTrait(success_result)
     ... # Up to date camera population
elif (cameraVersion >= 2 and cameraVersion < 1):
     trait = mediacreation.legacy.CameraTrait_v2(success_result)
     ... # V2 camera population
elif (cameraVersion >= 1):
     trait = mediacreation.legacy.CameraTrait_v1(success_result)
     ... # V1 camera population
else:
  raise RuntimeError()

# Spatial
if (spatialVersion >= 2 and spatialVersion < 3):
    trait = mediacreation.SpatialTrait(success_result)
    ... # Up to date spatial population
elif (spatialVersion >= 1):
    trait = mediacreation.legacy.SpatialTrait_v1(success_result)
     ... # V1 to date spatial population
else:
  raise RuntimeError()
```

### Benefits
- Maximally flexible, hosts and managers can disregard versioning for
  traits they don't care about.
- Obvious from the YAML which version a trait is.
- Individual traits will only update version when they change, thus they
  will not have "gaps", they will always go v1->v2->v3.
- A single trait can be updated in isolation without any effect on other
  traits in the package.
- Semver could be used to provide additional runtime compatibility
  information.

### Drawbacks
- Version has to be encoded in `traitID` because several methods
  (including `resolve`) take `traitSet`, which is only a collection of
  `traitIDs`. There is no `TraitsData` to inspect. This would be a major
  breaking change as currently conceived.
- Version support may become fragmented if hosts and managers provide
  versioned support for only certain traits
- When packing multiple traits, manager has to branch on each trait as
  they could be different versions.
- When extended to specification this _really_ causes problems, as we
  need to invent a new place to pack specifications version across the
  wire.

## Version the whole schema.
This option places a version number is placed at the top of the
`traits.yml` file or equivalent. This defines the version for all the
traits within the package.

The manager will still need a mechanism to know which trait-library
version the host will be expecting. This could be achieved by a
`HostInterface` method.

```cpp
//HostInterface implementation
SchemaVersion HostInterface::schemaVersion(std::string_view library_identifier) {
  if (library_identifier == "openassetio-mediacreation"){
    return openassetio_mediacreation::version();
  }
}
```
### Benefits
- Version dosen't need to be packed into any `traitId`
- A traits and specifications library gets a version as a unit, making
  talking about supported versions easier, and hopefully reducing
  support fragmentation
- Manager can branch at a higher level

### Drawbacks
- Unknown at runtime which traits or specifications have been updated in
  a version bump.
- Encourages redundant branching when in many/most cases traits will
  remain compatible between versions.
- Doesn't provide a way to enforce strict compatibility on a
  trait-by-trait basis programmatically, it's all or nothing.

```python
# The manager is responding to a resolve, needing to populate a
# TraitsData with a camera trait and a spatial trait of the expected 
# version
hostMediaCreationV = hostInterface.schemaVersion("openassetio-mediacreation")

...

success_result = TraitsData()
match hostMediaCreationV:
  case 1:
    camTrait = mediacreation.legacy.CameraTrait_v1(success_result)
    spatialTrait = mediacreation.legacy.SpatialTrait_v1(success_result)
    ... # V1 Camera + Spatial population
  case 2:
    camTrait = mediacreation.legacy.CameraTrait_v2_(success_result)
    spatialTrait = mediacreation.legacy.SpatialTrait_v2(success_result)
    ... # V2 Camera + Spatial population
  case 3:
    camTrait = mediacreation.CameraTrait(success_result)
    spatialTrait = mediacreation.SpatialTrait(success_result)
    ... # Up to date Camera + Spatial population
  case _
    raise RuntimeError()
```

### Last-Changed
A concept that kept coming up was the idea of a "last-changed" property
on the traits, when related to whole schema versioning, which we'll
just briefly mention.

```yml
# traits.yml
schemaVersion: 5

Camera:
  description: >
    The entity represents a device that captures a view through
    re-projection or encoding into some other form.
  usage:
    - entity
  last_changed: 2
```
- This would allow managers to support swathes of versions in a single
  branch, as the traits would remain compatible with eachother across a
  known set
- Opens the door up to more easily supporting automatic upgrade flows in the future
  given an injection of prewritten upgrade/downgrade methods.

# Worked Example
Let's work an example. Take the ever so popular `LocatableContent`
trait.


```yml
# Some descriptions omitted for brevity.
schemaVersion: 1 <------------ NEW

LocatableContent:
        description: >
          This trait characterizes an entity whose data is persisted
          externally to the API through data accessible via a valid
          URL.
          The `location` property holds the most applicable location
          of the entity's content for the current process environment
          - considering platform, host, etc. Location is in the form
          of a URL.
        usage:
          - entity
        properties:
          location:
            type: string
            description: ...
          mimeType:
            type: string
            description: ...
          isTemplated:
            type: boolean
            description: ...
```

Let's work through making a change to alter the name `location` to
`url`, to better convey that this string should be an url.

We will assume the schema is versioned as a unit for this example, but
it isn't so hard to imagine how this would look if the versions were
taken directly from the traits instead.

## Host
For context, the host code looks like this. The host is using the
version of `mediacreation` shown above, where `mediacreation` is on
version `1`. This won't change during this example.

```py
from openassetio.access import ResolveAccess
from openassetio_mediacreation.traits.content import LocatableContentTrait

...

resolved_asset = manager.resolve(
    entity_reference, {LocatableContentTrait.kId},
    ResolveAccess.kRead, context)
 url = LocatableContentTrait(resolved_asset).getLocation()  # May be None
```

## Manager
The manager needs to resolve this reference, and call the success
callback with the location.

```python
from openassetio_mediacreation.traits.content import LocatableContentTrait

def resolve(
        self,
        entityReferences,
        traitSet,
        resolveAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):

  success_result = TraitsData()
  trait = LocatableContentTrait(success_result)
  trait.setLocation(managed_filesystem_locations[ref.toString()])
  successCallback(idx, success_result)
```

At this point, `LocatableContent` has never had a version update, so
there is no need for the manager to do any version handling.

Now, let's make our change.
```yml
schemaVersion: 2 <------------ UPDATED

# Some descriptions omitted for brevity.
LocatableContent:
        description: >
          This trait characterizes an entity whose data is persisted
          externally to the API through data accessible via a valid
          URL.
          The `url` property holds the most applicable location
          of the entity's content for the current process environment
          - considering platform, host, etc. Location is in the form
          of a URL.
        usage:
          - entity
        properties:
          url: <---------------------- CHANGED
            type: string
            description: ...
          mimeType:
            type: string
            description: ...
          isTemplated:
            type: boolean
            description: ...
```
The manager sees this, and updates its mediacreation version. To support
hosts that use this new schema version, as well as hosts that havn't
upgraded yet, the manager now has to branch.

```py

def resolve(
        self,
        entityReferences,
        traitSet,
        resolveAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):

  hostMediaCreationV = hostInterface.schemaVersion("openassetio-mediacreation")

  success_result = TraitsData()
  if (hostMediaCreationV == 2):
    trait = mediacreation.traits.content.LocatableContentTrait(success_result)
    trait.setUrl(managed_filesystem_locations[ref.toString()])
    successCallback(idx, success_result)
  elif (hostMediaCreationV == 1):
    trait = mediacreation.legacy.traits.content.LocatableContentTrait_v1(success_result)
    trait.setLocation(managed_filesystem_locations[ref.toString()])
    successCallback(idx, success_result)
  else:
    raise RuntimeError()
```


## What about a non breaking change?

Good question. Up until now we've been demonstrating flat versioning for
brevity, but let's switch to semver for this example.

(Flat versioning may also support this, either via the OTIO approach of
just not updating the version for a minor breaking change, or having
`lastMajorChanged` and `lastMinorChanged` properties on traits.)

Lets take this example. Adding a new property `isLocal` to fulfil the
imaginary need to know if your content is on your local machine or not.
Going from where we left off
```yml
# Some descriptions omitted for brevity.
LocatableContent:
        description: ...
        usage:
          - entity
        properties:
          url:
            type: string
            description: ...
          mimeType:
            type: string
            description: ...
          isTemplated:
            type: boolean
            description: ...
          isLocal: <------------------ NEW
            type: boolean
            description: ...
        version: "2.1.0" <------------ UPDATED
```

With this being a non breaking change, the manager shouldn't have to
update. Imagine another host who is ahead of the manager, and has picked
up this new version.

```py
from openassetio.access import ResolveAccess
from openassetio_mediacreation.traits.content import LocatableContentTrait

...

resolved_asset = manager.resolve(
    entity_reference, {LocatableContentTrait.kId},
    ResolveAccess.kRead, context)

isLocal = LocatableContentTrait(resolved_asset).getIsLocal()  # May be None
```
Thankfully, we have already accounted for this. Our traitViews
understand missing properties, and return `None`/`Optional`, so the host
will know that there is no information on this new property from the
current version of the manager.

# Versioning Specifications
Traits are not all we have to consider, lets take a moment to think
about specifications.

```yml
# For example, Workfile, A specification with the Entity, Work, and LocatableContent traits.
Workfile:
  description: >
    The entity is the product of some manual task or process,
    that often defines how to produce or derive other data.


    Common examples are the documents opened, worked on and saved
    by artists using DCC tools to create models/images/etc.
  usage:
    - entity
  traitSet:
    - namespace: usage
      name: Entity
    - namespace: application
      name: Work
    - namespace: content
      name: LocatableContent
```

Conceptually, specifications are "things" that exhibit a set of traits.
Current, specifications are purely unordered sets of `traitId`'s, raising similar problems as how to encode the version that individual traits have.

Specifications are used to categorize entities when performing api operations. For example, they may be used to filter an asset browser to specific kinds of entity (Image, Video, TextDoc, etc). They are also used in publishing, where both host and manager have to agree on the "kind of thing" being published.

Initially, one would want to version these things with the same
mechanism to traits, with the version being updated when the `traitSet`
of the specification is modified. However, what happens if a trait in
the specification is merely versioned up, should this imply a
specification schema version increment?

Tentatively, no, or at least, it would be better if it didn't. The
method of versioning plays into this decision quite strongly:

### Versioning entire schema
- Has the advantage that version bumps are always together, so if a
  trait updates, the specification implicitly updates with it.
- Much simpler to think about, the specification version in-play is
  always the one the manager reports.
- Don't have to find a way to pack specification version into `traitSet`
- Makes discoverability extra difficult for managers that are trying to
  support ranges of compatible versions with fewer branches.

### Versioning specs individually
- Raises the question of whether each trait in a specification needs to
  be pinned to a specific version of a trait.
- Have to pack specification version into the type, or ask the manager
  to somehow deduce specification version

The complexity of thinking about disconnected versioning when you take
specifications into account does seem to bias towards versioning the
entire schema as a unit.


# What about multi-package
The ecosystem and thinking around multi-package specifications isn't
very developed yet, but nonetheless will be impacted by this decision.

Consider another traits and specifications library alongside
`openassetio-mediacreation` called `companycorp-traits`. You could build
a specification :

```yml
 CompanyCorpCamera:
    description: >
      Any entity that holds three-dimensional data.
    usage:
      - entity
    traitSet:
      - namespace: openassetio_mediacreation.imaging.Camera
        name: Camera
      - namespace: companycorp-traits.identifier
        name: CompanyCorp
```

This is troublesome to consider for a few reasons. It's tempting to just
handwave this sort of thing away for later due to how complex it can
get, but no, let's bite the bullet.

## Explicit versioning
If we were to explicitly version specifications, this could work quite
well, specifications would carry with them their specific versions, as
well as the specific versions of the traits contained within them,
allowing version branching irrespective of the source of the trait.

```yml
 CompanyCorpCamera:
    description: >
      Any entity that holds three-dimensional data.
    usage:
      - entity
    traitSet:
      - namespace: mediacreation.imaging.Camera
        name: Camera
        version: 2
      - namespace: companycorp-traits.identifier
        name: CompanyCorp
        version: 3
    version: 2
```

It seems necessary in this conception that any version update to a trait
also versions the specification. This is very direct, and allows although
all the same technical downsides to explicit spec versioning apply.

## Whole-schema versioning.
The story of handling a cross-schema trait with versioned schemas
becomes complex fast. Not only do you need to query the host for schema
versions for every trait in the specification, you also need to query
the host for the schema version of the specification itself, which may
be defined in a third package entirely.

Consider :
```python
#Rough psuedocode
specVersion = hostInterface.getSchemaVersion(CompanyCorpCamera.getPackageIdentifier())
switch (specVersion):
  case 1:
    handleTraitVersionsForSpecV1(successCallback, errorCallback)
  case 2:
    handleTraitVersionsForSpecV2(successCallback, errorCallback)

def handleTraitVersionsForSpecV1(successCallback, errorCallback):
  cameraTraitVersion = hostInterface.getSchemaVersion(legacy.CompanyCorpCameraV1.Camera.getPackageIdentifier())
  companyCorpTraitVersion = hostInterface.getSchemaVersion(legacy.CompanyCorpCameraV1.CompanyCorp.getPackageIdentifier())

  # You still have to version iterate over each trait individually, because you can't assume they came from the same package.
  switch (cameraTraitVersion):
    case 1:
      ... # Camera trait version 1 behaviour
    case 2:
      ... # Camera trait version 2 behaviour

  switch (companyCorpTraitVersion):
  case 1:
    ... # CompanyCorp trait version 1 behaviour
  case 2:
    ... # CompanyCorp trait version 2 behaviour

def handleTraitVersionsForSpecV2:
  ... #Same again but slightly different spec structure.
```

As you can see, this isn't going to be a good time. Which is a shame
because in all other cases except for split-package specifications, a
single schema version has seemed the simplest option.

The main problem however is the generated specification views have
utility methods on them to create the trait views that they should
contain. This introduces a sticky build dependency that would need to be
removed, likely by removing the utility methods overall.

## Simplify, bundle everything.
A solution that came up when trying to wrap our heads round this was the
idea of not allowing cross-package specifications as such, but to
instead achieve composition via bundled packages.

In this conception, when you generate your trait and spec views, you
would provide the `.yaml` of all the other packages you are referencing,
essentially duplicating them into a new, unique package.

`openassetio-traitgen -o output -g python --deps
openassetio-mediacreation/traits.yml companycorp_traits.yml`

This would essentially create a brand new traits package with it's own
unique trait identifier `companycorp-openassetio-mediacreation`, which
could then be treated as a single package, sidestepping _all_ the
complexity without removing the ability to compose cross package traits.


This would strongly put multi-package specifications into the camp of
being an extension method used by organizations wishing to use
openassetio inside their private pipeline, as it's doubtful productized
management systems or hosts would want to account for all the specific
permutations here. A major downside.

## Simplify, ignore it.
Also an option, maybe we can think about this later. How and if external
organizations are going to use non-mediacreation trait libraries is
still an open question.

# Conclusion?
As yet undecided.

The simplest solution that will help people seems to be providing
manager plugins with an introspection method that lets them query the
schema version of the traits and specifications packages in use by the
host.

This has the unfortunate effect of breaking the cross-schema
specification view classes due to the package dependencies that the
classes were built against potentially mismatching the packages in use
by the host. It is however possible to break this dependency by removing
some of the non-essential utility of the specification view classes.