# DR003 ManagerInterface method naming

- **Status:** Decided
- **Impact:** Small
- **Driver:** @foundrytom
- **Approver:** @feltech @foundrytom @TomFoundry
- **Contributors:** @feltech @foundrytom @TomFoundry
- **Outcome:** Mostly maintain singular method names

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
* `preflight` -> `preflightMultiple`
* `register` -> `registerMultiple`
* `resolveEntityReference` -> `resolveEntityReferences`

Other methods that we (may) aim to refactor into accepting bulk queries
are

* `managementPolicy`
* `isEntityReference`
* `entityExists`
* `defaultEntityReference`
* `entityName`
* `entityDisplayName`
* `getEntityMetadata`
* `setEntityMetadata`
* `getEntityMetadataEntry`
* `setEntityMetadataEntry`
* `entityVersionName`
* `entityVersions`
* `finalizedEntityVersion`
* `getRelatedReferences`
* `setRelatedReferences`
* `thumbnailSpecification`

## Options considered

### Option 1

Singular Convention

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small

### Option 2

Singular entity prefix convention

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small

### Option 3

No entity prefix convention

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small

### Option 4

Plural Entities Convention

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small

### Option 5

Plural Noun Convention

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small

## Outcome

Summarize the outcome, stating which option was chosen and why.