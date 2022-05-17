# Recording user facing changes in CHANGES.md

We make use of a `CHANGES.md` file to record user-facing changes between
versions. This file must be updated directly in any commits that cause
some public change of behavior.

This approach has the advantage that the file is always up to date, and
accurately reflects exactly what has been merged into a release branch.
If a commit is ever rolled-back, there is no danger of the change log
getting out of sync.

## What counts as a "user facing change"?

Anything other than an internal implementation detail. This could
include:

- New features.
- Changes to the behavior of existing features.
- Changes to public API signatures or methods (including exposed test
  infrastructure).
- Changes to library ABIs.
- Changes to runtime dependencies.
- Changes to supported platforms.
- Changes to the distribution format.

There is no need to include:

- Refactoring or restructuring that has no effect on behavior or the
  public surface area.
- Changes to the build pipeline or CI infrastructure.
- Changes to user facing behavior that has not yet been released
  (assuming any existing change log entries from its introduction are
  still valid).

## Formatting

The change log takes a very simple format, as illustrated below, using
the past tense:

```markdown
Changes
=======

v2.0.0
------

### Breaking changes

- Split `Specification` class in to `SpecificationBase` and `TraitsData`
  [#348](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/348).


### New features

- Added `TraitBase` Python class to be used for all custom traits.


### Improvements

- `TraitsData` now supports post-construction addition of traits.
- `TraitsData` `setTraitProperty` now automatically adds the trait if it
  has mot previously been set.


### Bug fixes

- `Session` no longer keeps `ManagerInterface` instances alive after the
  current manager has changed.


v1.2.0
------

### New features

- Added `OPENASSETIO_NS(InfoDictionary_size)` method to the C API to
  allow the number of keys in an `InfoDictionary` to be obtained.
```

1. The file should have a single level-one heading `Changes` and use the
   `=` (equals) markup.
2. Underneath this, and separated by one blank line, should be a level-2
   heading for each release version, using the `-` (hyphen) markup.
3. For each version, changes should be grouped into the four
   standardized categories noted below, using the `###` markup. With a
   single blank line below the heading, and two blank lines at the end
   of each section.

### Change categories

All entries should be grouped into one of the following sections. Each
section should only be added when there is at least one change of that
type in the release:

- **Breaking changes**: For any changes that cause an incompatibility
  with a previous version. [Major releases only]
- **New features**: For any changes that introduce new behavior (as
  opposed to changes to existing functionality). [Major/Minor releases
  only]
- **Improvements**: For any changes that modify existing behavior, or
  don't warrant the 'glamour' of being a fully-fledged feature.
  [Major/Minor releases only]
- **Bug fixes**: For fixes to incorrect behavior of a previous release.
  If this results in a breaking change to behavior, then they should
  only appear in Major release versions, otherwise then can appear in
  any release.

### Change entries

- Each change entry should concisely describe each change using the past
  tense.
- Text should be written from the end-user perspective using only public
  business language.
- Back-tick markdown should be used for any API or file references, or
  any value literals.
- Changes should include links to any relevant GitHub issues. Links to
  User Stories are preferred to Pull Requests.

## How to add your changes

As work continues towards a release, due to SemVer, the precise version
of the next release is generally unknown until the release is made. At
which point the version will be defined by the greatest severity of
change in that release.

As such, whenever you add a change to the `CHANGES.md` file as part of
development, it should always be under a `vX.X.X` for the version at the
top of the file. If you are the first to add a change, simply create
this version heading as part of your commit.

The use of a placeholder version also helps make it clear that these
changes are yet to be released.

### A note on maintenance branches

As we employ a merge-forward strategy for maintenance, changes on
maintenance branches should be under a version heading that only
contains placeholders for the elements of the version that are allowed
to change, ie: `v3.X.X` or `v3.2.X` - depending on the release strategy.

The change log should maintain strict chronological ordering for
releases, and so any placeholder versions should always be at the top of
the file.

> NOTE: When merging-forward, it is critical to ensure that the change
> entries from the source branch are also copied into the appropriate
> version in the target branch.

## Making a release

When all commits for a release are in, there should be a single final
version bump commit. This should replace the version placeholder string
with the final release version, along with any other repository
constants that reference the version.

The release tag should then be made from this commit.
