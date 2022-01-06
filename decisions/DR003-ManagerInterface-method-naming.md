# DR003 ManagerInterface method naming

-   **Status:** Decided
-   **Impact:** Small
-   **Driver:** @foundrytom
-   **Approver:** @feltech @foundrytom @TomFoundry
-   **Contributors:** @feltech @foundrytom @TomFoundry
-   **Outcome:** Mostly maintain singular method names

## Background

A manager plugin must implement the `ManagerInterface` in order to allow
the Asset Management System to be queried by a host.

Through various discussions we have determined that most of
the `ManagerInterface` methods should accept a list for their primary
parameter(s) (usually entity references) and then return a list of
responses, i.e. act as a bulk/batch query. We will then add some
convenience mechanism wrapping these bulk queries in a singular
variant.

The question we're then faced with is what should the methods under
`ManagerInterface` be named? Currently, most of the methods are solely
singular, but some have plural variants.

## Relevant data

This work originated from a [discussion](https://github.com/TheFoundryVisionmongers/OpenAssetIO/discussions/37),
which instigated an [issue](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/43)
to address concerns over bulk query primacy.

The methods that currently have plural variants are

-   `preflight` -> `preflightMultiple`
-   `register` -> `registerMultiple`
-   `resolveEntityReference` -> `resolveEntityReferences`

Other methods that we (may) aim to refactor into accepting bulk queries
are

-   `managementPolicy`
-   `isEntityReference`
-   `entityExists`
-   `defaultEntityReference`
-   `entityName`
-   `entityDisplayName`
-   `getEntityMetadata`
-   `setEntityMetadata`
-   `getEntityMetadataEntry`
-   `setEntityMetadataEntry`
-   `entityVersionName`
-   `entityVersions`
-   `finalizedEntityVersion`
-   `getRelatedReferences`
-   `setRelatedReferences`
-   `thumbnailSpecification`

## Options considered

| Current Name             | Option 1                  | Option 2                     | Option 3                     |
| ------------------------ | ------------------------- | ---------------------------- | ---------------------------- |
| `isEntityReference`      | `areEntityReferences`     | `isEntityReference`          | `isReference`                |
| `defaultEntityReference` | `defaultEntityReferences` | `defaultEntityReference`     | `entityDefaultReference`     |
| `getRelatedReferences`   | `getRelatedReferences`    | `getRelatedEntityReferences` | `getEntityRelatedReferences` |
| `entityName`             | `entityNames`             | `entityName`                 | `entityName`                 |
| `entityVersions`         | `entityVersions`          | `entityVersions`             | `entityVersions`             |

### Option 1

Batch methods should have plural names.

#### Pros

-   Intuitive for people that are unfamiliar with OpenAssetIO
    conventions.
-   Easy to see whether a given method is batch or singular.
-   Method names read like natural English.

#### Cons

-   Plural method names introduce ambiguity. For example, `entityNames`
    and `entityVersions` look similar, but they are semantically
    different.  For `entityNames` there are multiple entities and each
    has one name, while for `entityVersions` there are also multiple
    entities but each has multiple versions. We could disambiguate this
    by making changing the pluralization to `entitiesName` and
    `entitiesVersions`, but this leads to method names that are ugly and
    hard to read.

### Option 2

Batch methods should have singular names (i.e. there is no naming
convention to differentiate batch & non-batch methods).

#### Pros

-   Unaffected by the ambiguous pluralization problem described above
    (see [Option 1](#option-1)).
-   Method names read like natural English.

#### Cons

-   Potentially confusing for newcomers unfamiliar with OpenAssetIO
    conventions.
-   Whether a method is singular or batch cannot be inferred from the
    method name. However, given that most `ManagerInterface` methods
    (including all its methods related to entities) will be batch
    methods, this is unlikely to create much confusion.

### Option 3

Batch methods should have singular names. And methods that relate to
entities should have the prefix "entity". For example, method
`defaultEntityReference` in [Option 2](#option-2) would instead be
`entityDefaultReference`. For methods with a verb prefix, the entity
prefix should go after the verb (e.g. `getEntityRelatedReferences`).

#### Pros

-   Unaffected by the ambiguous pluralization problem described above
    (see [Option 1](#option-1)).
-   Obvious which methods are related to entities, and which are not.

#### Cons

-   More difficult to explain than [Option 2](#option-2)
-   Requires use of "Reference" instead of "EntityReference", in order
    to prevent illegible names. For example,
    `getEntityRelatedReferences` is more readable than
    `getEntityRelatedEntityReferences`, but for consistency, this would
    also require changing `isEntityReference` to `isReference`.
-   Method names do not read like natural English.

## Outcome

We choose [Option 2](#option-2), batch methods should have singular
names. This is preferred to [Option 1](#option-1) because it doesn't
lead to the ambiguous pluralization problem. And it is preferred to
[Option 3](#option-3) because it is simpler, and leads to more readable
method names.

