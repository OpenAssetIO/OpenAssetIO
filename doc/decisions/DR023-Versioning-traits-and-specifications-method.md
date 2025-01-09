# DR023 Trait & Spec versioning paradigm, in-data or out-of-data.

- **Status:** Decided
- **Impact:** High
- **Driver:** @elliotcmorris
- **Approver:** @felltech @elliotcmorris @themissingcow
- **Outcome:**

## Background
This DR follows on from a [previous attempt at a
DR](https://github.com/OpenAssetIO/OpenAssetIO/pull/1254), which sought
(somewhat haphazardly), to nail down format and type of versioning that
traits and specifications libraries would use. That draft DR, in
hindsight, attempted to tackle too broad a range of decisions, and
consequently ended up deciding on not much. Nonetheless, we are now more
informed and are coming back for a second attempt.

This DR attempts to narrow the focus onto a single point of contention
that became a recurring theme, whether OpenAssetIO trait and
specification versioning information should be communicated as part of
the data, or agreed upon as a secondary "handshake" interaction between
host and manager. For the purposes of this DR, we will refer to these
two categories as "in-data" and "out-of-data".

In attempting to keep its scope limited, this DR does not propose a
specific solution, but merely provides representative examples of
what a solution in each proposed paradigm might look like. It is generally
assumed further facilitative work (for example, convenience utilities
in `traitgen` and `mediacreation` will be decided upon and implemented
at a later date.)

## Relevant data

Over the course of our investigations, it became clear that we had
either failed to consider entirely, or handwaved away as less important
than they actually were, several key criteria in the name of simplicity.
The main themes are listed below, as we currently understand them.

### Two way compatibility
In the [previous
DR](https://github.com/OpenAssetIO/OpenAssetIO/pull/1254), we attempted
to make a simplifying assumption based around the idea that managers
were more capable of managing version updates. Whilst we still believe
that, it has come to our attention that there are valid reasons that a
host would also want to maintain backwards compatibility when updating
versions. Due to this, we now consider the ability for both the host and
manager to choose to maintain compatibility essential.

### Distributed workflows/RPC
During investigations, the concept of systems that work remotely, (eg
[gRPC](https://github.com/foundrytom/OpenAssetIO-gRPC)) came up as a
potential difficulty with some implementations, given that any callback
based communication, ie querying the `hostInterface` for a version,
would be especially difficult to implement in this paradigm.
We now consider it essential that we take an approach where versioning
does not impose undue extra effort on distributed workflows.

### No internal state
OpenAssetIO has long attempted to stick to the philosophy that each
method call represents a stateless interface, and that the manager
should not persist state between calls. This is true and essential to
model potential workflows/integrations in the future (GRPC/HTTP), etc.

However, we do not believe this necessarily excludes any handshake style
interactions. OpenAssetIO already provides a mechanism to configure
managers at the beginning of the session with
[initialize](https://docs.openassetio.org/OpenAssetIO/classopenassetio_1_1v1_1_1host_api_1_1_manager.html#aa52c7436ff63ae96e33d7db8d6fd38df).
Whilst we agree that state must not be utilized during a session,
injecting version state before or at initialize time remains a valid
option.

### Naive managers
A pitfall that many of our earlier sketches fell into was assuming
managers would have a first class understanding of the traits they were
being asked to persist, which led to us assuming they would be able to
perform upgrade and downgrade behaviour on them.

This isn't, nor has it ever been this case, and the idea that a manager
can and should persist data it doesn't understand has been a long held
principle of the library. This supports the idea stated above that both
hosts and managers must each be able to adapt to version divergence, as
it cannot be known which of them understands the data, and thus
understands how to perform the migration.

### Is versioning optional?
Some concerns have been raised about the optionality of versioning,
specifically around the idea that a complicated versioning handshake may
lead to implementors simply ignoring it, a valid concern. Whilst we can,
and likely will declare at least some support for versions a necessary
part of any implementations, we have seen before that implementors can
ignore necessary implementational steps due to ignorance of their
necessity. This point is well taken, and will weigh into any decisions.

### Reconsidering schema version
The achilles heel of decision records ... interconnected concerns. the
prior DR attempt _tried_ to isolate itself to higher level concerns,
version format, schema vs trait version, etc. One of the decisions we
_thought_ we made was deciding on schema versions (as opposed to trait
by trait versions).  However, choosing to place the version in the data
makes us reconsider the value of schema-wide versions. They are simpler
conceptually, but if each trait could come in with a different schema
version anyhow, are we really gaining much by avoiding every trait
simply having its own version?

## Options considered

### Option 1 - Out of data

This option imagines that an agreement is made via the OpenAssetIO
interface on the version of traits and specifications that are in
play. Hosts and Managers will inspect each other, and make a "handshake"
deal on agreed versions. From that point on, the versions are known
by both sides, and both sides must communicate using data formatted
to the schema of the agreed upon version.

Our initial, "what is the simplest thing we could do" was the idea that
the host knows the versions in play right? Let's just add a way for
the host to let the manager know what versions it wants to use, and let
the manager adapt. See example below.
### Host side
```python
# When setting up a manager
settings = manager.settings()
settings["server"] = "my.server.com"

mediacreation_version = openassetio_mediacreation.version()

manager.initialize(settings, [mediacreation_version])
```

### Manager side
```python
 def initialize(self, managerSettings, schemaVersions, hostSession):
   # Store versions for later use
   self.__schemaVersions = schemaVersions
```

If you've read the principles above, you can likely see that this
violates a few of them. Notably, the host has no method of supporting
multiple versions, and all the onus of migrating between versions is on
the manager, despite the fact that it may not understand it at all.

Therefore, an out-of-data implementation will likely be a fair bit more
complicated, and look more like a **negotiation**.

### Negotiated

In this conception, one side of the exchange (manager in this case),
advertises a set of versions it supports. The other side then queries
this list, selects the specific versions it would prefer to communicate
in, then informs the other side which versions should be the medium
of exchange going forward. Keep in mind, this is merely a passable
representation of the concept of a negotiated, out of data approach,
and not a final design.

### Host side

```python
# During initial setup

# In this example, supportedSchemaVersions returns a dictionary of the
# provided schemas, mapped to a list of versions the manager supports
# for those schemas
# {
#   "openassetio.mediacreation", [1,2,3]
#   "companycorp.custom_traits", [1]
# }
supported_versions = manager.supportedSchemaVersions()

# Verify that the trait packages we require are supported at all
# by the manager
if not openassetio_mediacreation.packageId() in supported_versions:
  incompatible_with_manager_error()
  return;

if not companycorp_traits.packageId() in supported_versions:
  incompatible_with_manager_error()
  return;

mediacreation_version = None
companycorp_version = None

# Verify the versions of the trait packages we are capable of supporting
# are supported by the manager
# This host is capable of working with mediacreation version 3 and 4,
# and companycorp custom traits version 1. Given the choice, it would
# prefer to work with mediacreation version 4.
if 4 in supported_versions[openassetio_mediacreation.packageId()]:
  mediacreation_version = 4
else if 3 in supported_versions[openassetio_mediacreation.packageId()]:
  mediacreation_version = 3
else:
  incompatible_with_manager_error()
  return

if 1 in supported_versions[companycorp_traits.packageId()]:
  companycorp_version = 1
else:
  incompatible_with_manager_error()
  return

# Tell the manager up front what versions you are going to use.
# These must be versions reported from `supportedSchemaVersions`.
negotiated_schema_versions =
{
  openassetio_mediacreation.packageId():mediacreation_version,
  companycorp_traits.packageId():companycorp_version
}
manager.informSchemaVersions(negotiated_schema_versions)

... # Go on to use openassetio methods with trait views of the now
    # agreed upon version for each trait package.
```
### Manager side
```python
def supportedSchemaVersions(this, hostSession):
  # As a manager, we can likely directly declare which schema versions
  # we support
  return {
   openassetio_mediacreation.packageId(), [1,2,3]
   companycorp_traits.packageId(), [1]
  }

def informSchemaVersions(this, schemaVersions, hostSession):
  # Record the schema versions that the host is going to use.
  # We can use these to branch our internal functionality
  this.__mediacreation_schema_version = schemaVersions[openassetio_mediacreation.packageId()]
  this.__companycorp_schema_version = schemaVersions[companycorp_traits.packageId()]
```

### Pros
- Decides on version up front, reducing low level trait by trait branching.
- Versioning is technically optional, which may allow "best-effort" data
  access. E.g. if the trait ID remains unchanged, and only new
  properties are added, then a trait version bump is a non-breaking
  change - `isImbued()` still returns `true` and older trait properties
  are still accessible.
- Specifications continue to work as they are currently conceived. If
  both host and manager agree on the schema version, then the valid
  selection of Specification view classes is trivially known.

### Cons
- Complex dance needs to be done up front, people may end up just
  skipping it.
- The potential to deliberately skip version negotiation to allow "best
  effort" access patterns is very bug-prone, may be difficult to debug,
  and in general introduces confusion about whether versions should be
  accounted for.
- Managers and hosts now have additional data related to specific
  entities that they must communicate, increasing the complexity of
  "pass-through" hosts and managers, and complexity of data transfer
  across multiple hops and/or storage in multiple systems. This could be
  especially problematic for naive managers that simply wish to be data
  recorders, as they are almost forced to be version aware.
- Implies probable negotiation, which implies introducing state.
  See [no internal state](#no-internal-state).
- Precludes the ability to communicate with multiple versions of the
  same trait in the same session.
- Upgrading traits requires out-of-code knowledge about what traits
  are compatible between schema versions.
### Option 2 - In data

In this conception, version information is sent "over the wire" so to
speak. Each trait has a version packed into it, which is unpacked on
the other side, and then used for any version branching.

> **Note**
>
> Practically, this would likely be packed into the `traitId` of each
> trait, something like
> "`openassetio-mediacreation-v-4:LocatableContent`". This would
> effectively make each version of a trait a new trait as far as the
> `openassetio` core library is concerned.


### Host side
```python
# The host side implementation is almost entirely unchanged from
# from standard, excepting a new BatchElementError type
trait_set = {LocatableContentTrait.kId}
context = self.createTestContext()

result = [None]

def success_cb(idx, traits_data):
    result[0] = traits_data

def error_cb(idx, batchElementError):
    if instanceOf(batchElementError, VersionNotSupportedError):
      incompatible_with_manager_error()
    ...

self._manager.resolve(
    [entity_reference], trait_set, ResolveAccess.kRead, context, success_cb, error_cb
)
```
### Manager side
```python
# On the manager side, each trait gets unpacked (probably via a utility
# method provided by traitgen or openassetio), and branching is done
# on a trait by trait basis

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

  # This function is imagined a pre-provided utility, possibly generated
  # via traitgen, that would error in some way if the trait set does not
  # contain the locatableContent trait.
  locatableContent_version = locatableContent_version_from_trait_set(traitSet)

  success_result = TraitsData()
  if (locatableContent_version == 2):
    trait = mediacreation.traits.content.LocatableContentTrait(success_result)
    trait.setUrl(managed_filesystem_locations[ref.toString()])
    successCallback(idx, success_result)
  elif (locatableContent_version == 1):
    trait = mediacreation.legacy.traits.content.LocatableContentTrait_v1(success_result)
    trait.setLocation(managed_filesystem_locations[ref.toString()])
    successCallback(idx, success_result)
  else:
    raise RuntimeError()

```

#### Pros
- More flexible, traits of different versions can be mixed in the same
  session, which could allow hosts/managers to perform partial upgrades
  in the case they are blocked on small specifics, and allow components
  of a system to each work with a different schema version and merge
  their results.
- Hosts and managers would be capable of working with mismatched
  schema versions, so long as the versions of the individual required
  traits are compatible.
- Hosts don't have to interrogate and declare which library versions
  are in use, which helps especially in the case of second-order
  dependencies.
- Seems to fit with existing OpenAssetIO design, especially with
  `BatchElementError`, as an incompatible version wouldn't necessarily
  need to error the whole batch.
- No new API, core `openassetio` library remains version unaware.
- Cannot be ignored, unlike other "layered on top" mechanisms.
- Managers not required to consider storage/communication of additional
  version data to enable interpretation by future/downstream systems.
- Stateless by default.
- Allows per-trait versioning, which avoids the need for "insider
  knowledge" as to which traits actually change in which package
  versions.
- Prior art (e.g. OTIO) encodes versions in their data structure,
  presumably for good reason.
- Allows 'simple' hosts to be written that don't understand specific
  data, and thus wouldn't be able to meaningfully negotiate.

#### Cons
- No "primary" version across the session, increasing implementation
  complexity.
- Would likely require some utilities in `traitgen`, otherwise, due to
  each new version effectively being a brand new trait, constructing the
  correct trait view would be become a tedious dance.
- Introspection methods become more complex (see [What's
  versioned](#whats-versioned)).
- Unclear how specification versioning is to work without an out-of-data
  version.
- The most obvious implementation, (using `traitID` to store the
  version), would effectively make any change to a trait version a
  breaking change. Allowing non breaking changes (such as adding a new
  property) would require significant rework to the `traitgen` output.

### In data - Extended
The implementation of in-data versioning is very basic, which is part of
its strength, but it necessitates a "try and see" approach on the part
of the host. If the host wants to be adaptive to the manager, it may
benefit from a more up front introspection of the supported manager
versions.

To this end, the `supportedSchemaVersions` method (or similar concept,)
from Option 1 could be orthogonally added without any conceptual
conflict. This would have the added benefit of allowing hosts to also
support a range of version/have backwards compatibility, which is a huge
benefit.

This stops short of negotiation, being merely introspection similar to
our other manager introspection methods.

### What's versioned?
In this example, we have been working under the assumption that we'll be
inserting version info into `traitId`, which in the current environment
essentially makes each new version of a trait a unique trait, which has
both pros and cons.

A decision intentionally not made in this DR is whether or not this sort
of presumption is the way forward with an in-data approach. it is
possible to pack version data into `traitID` and yet not presume that
`mediacreation-v1-locatableContent` is a conceptually different trait
from `mediacreation-v2-locatableContent`.

There are reasons we might want to do this, for example `entityTraits`
and perhaps even `managementPolicy` could potentially benefit from being
unversioned. Does a user want to know that an entity supports
`locatableContent-v2` specifically, or are we simply asking "What is
this thing?", in which case, an unversioned, or "all-version" method of
talking about traits may be helpful.

`managementPolicy` presents a unique decision point with an in-data
solution, as it is supposed to be entity agnostic, which could present
problems to a simple manager if we choose to follow the implications
of versioning it.

We intentionally leave this choice to a subsequent decision, as there
are numerous technical options available.
## Decision

OpenAssetIO will move forward with [Option 2 -- in
data.](#option-2---in-data)

### Rationale.
This has been a very complex decision, and is only a subset of a larger
strategy, many decisions remain to be made before versioning can be said
to be complete, and in many ways versioning will not be complete until
after real world usage has hardened our approach.

Once the non-negotiable preconditions had been considered, the
controversy in the decision came down to four general areas

- The addition of state to the interface.
- The possibility and ease of naive host/manager implementation.
- The possibility and ease of exchanging different versions in the same
  session.
- What to do about specifications.

There were of course other points, but on all but the latter of these
points of contention, an in-data solution came out ahead.

The question of specifications is a large one, and can be said to be
out-of-data versioning greatest appeal at this point. We will move
forward under the assumption that specifications will remain
un-versioned (in the sense that specifications themselves will not have
an in-data version number, the traits within them will implicitly be
versioned). This may introduce complexity to implementors using
specification views in their applications, and they may need to resort
to using out-of-code knowledge to resolve compatibility issues. The
working view of specifications however is that they are merely optional
implementor conveniences, and seeing as they have no real presence in
the API itself, we feel comfortable enough putting them to the side for
this decision, although there is certainly more thinking to be done
here.

Nonetheless, a large reason for the adoption of an in-data solution is
how little of the API it needs to disrupt in order to become useful, and
yet how open it is to extension.

We acknowledge there may be complexity challenges by moving forward with
direct in-data versioning with current OpenAssetIO methods, as the idea
that each version of a trait effectively becomes a new trait introduces
[questions](#whats-versioned) with introspection methods. However, the
fact that the solution will function under present assumptions without
the need for _any_ API changes is very appealing, and allows a layered
iterative approach to reduce this complexity, rather than having to do a
big bang drop full of speculation all at once. We look forward with
excited expectation as to how `openassetio-traitgen`, with its generated
views, can be leveraged to make this experience simpler and easier.
