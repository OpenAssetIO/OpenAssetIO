# Commit guidelines

## What makes a good commit

A good commit should be a small, self-contained change to a vertical
slice of the code base, that leaves it in a working state.

For bigger changes, layering functionality from the inside towards a
public interface may facilitate more granular work. For example:

 1. A commit to add an (tested) internal method for something.
 2. A commit to add (tested) public functionality that uses the new
    API.

This may seem be at odds with some TDD based workflows. See the
[TDD workflows and commit granularity](#tdd-workflows-and-commit-granularity)
section below for more details on this.


### Pre-push check list

Before pushing any commits upstream, give them a quick proof read and
double check:

 - You have a suitable [CLA](PROCESS.md#contribution-sign-off) in
   place.
 - All your commits are signed-off and signed (using `-s` to accept the
   [DCO](PROCESS.md#contribution-sign-off), and
   [GPG](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
   signed to verify your identity).
 - Each commit only affects a single logical unit of work.
 - The documentation has been updated accordingly to cover your changes.
 - There is no dead, commented out or placeholder code.
 - There are no stale comments from the previous implementation.
 - There are no stray changes that should be in another commit.
 - There are no inadvertent white space or other changes to unrelated
   areas of the files.

If you want to take the opportunity to clean up minor cosmetic issues
(such as spelling/white space/etc.) as part of your work, this is fine,
just do them in their own commit. This makes it clear what is an
intended change vs an accidental one.


## Commit Messages

Commit messages are a vital part of code archaeology, they serve as a
TL;DR and to record rationale for a change. Think of them as
light-weight decision records.

We use the [50/72](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
format for Commit messages. This aims to make them readable in the
widest variety of scenarios. In addition, we have a few other
conventions.

Titles should be no more than 50 characters, and written in the
imperative tense. If applicable, the component being changed should be
used to prefix the message:

```
[<component>] <Imperative tense change>
```

For example:

```
[Docs] Fix spelling mistake in introduction
[Core] Ensure data flushed to disk on exit
```

See the [appendix below](#appendix---code-components) for a list of common
components.

> IMPORTANT: Do not put GitHub refs in the title - they belong in the
> body.

The body of the message should be line wrapped at `72` characters. It
should be a light-weight decision record, consisting of:

 - A high-level description of the main changes.
 - The rationale for making them.
 - Notes on any peculiarities not covered by in-code documentation.
 - Notes on any rejected alternatives.
 - A reference to the GitHub issues(s) related the work.

Imagine yourself coming to a change fresh, in two years time, trying to
work out _why_ it was done. You have the diff, and in-code comments to
cover the majority of what changed. The information that usually gets
lost is why, and also why a different approach wasn't taken.

> NOTE: Commit message for transient review-only commits should be
> prefixed with `fixup!` or `squash!`. See the notes below for more
> information on when to use these.


## TDD Workflows and commit granularity

In TDD it is common to write failing tests, then evolve the
implementation until tests pass. Often starting from the very outside
with end-to-end tests. How does this fit in with the rule of 'the build
should always work between commits' and 'no broken public interfaces'?
There are two answers to this, depending on how large the intended
change is.

### Every-day changes

If the work can comfortably be completed within a single Pull Request
(and so there would be no broken public interfaces once merged), we make
use of the `squash!` technique. The contributor can opt to structure the
Pull Request such that it presents a series of easy to review commits
that follow the TDD cycle, even if they break the build from step to
step. These commits should be prefixed with suitable markup to denote
that they are to be squashed together before the request is merged into
a release branch.

> IMPORTANT: Commits of this nature should always be prefixed with
> `squash!`. If you then reference the title of the target commit, you
> can use `git rebase -i --autosquash` later to collapse these down
> automatically, combining all commit messages into one.
>
> Use the body of the message to describe the specifics of each commit.

```
[API] Add `/stores` endpoint                     # API definition and tests
squash! [API] Add `/stores` endpoint             # Endpoint/Handlers/Domain implementation
squash! [API] Add `/stores` endpoint             # Repository implementation
[CLI] Add `store` noun and `add`/`delete` verbs  # Test + Implementation
```

In the above example, the larger chunk of work implementing an API has
been split into several commits for TDD and readability. The commit body
would describe the specifics of what has been done in that commit. These
three commits would be squashed before merge, after review. The title of
the first commit should reflect the final merged commit title.

The CLI changes have been made as a single commit containing tests and
implementation due to the simpler nature of that work. This commit would
be left as a separate commit after merge, as adding the API, then
binding it to the CLI are two logically separate things.

The benefit here is that if the CLI commit needed to be rolled back due
to a bug, it would then allow the API to remain functional (assuming
there was no issue there).

It's also worth noting that the contributor may have started with a
completely different set of working commits before the Pull Request was
made. The commits shown below were easily rearranged into the preferred
sequence and granularity for review using an interactive git rebase.
This allowed the 'end-to-end first' development approach to be used,
without compromising the functionality of the release branch post merge.

```
[CLI] Add e2e test for store verbs
[CLI] Add store verb commands
[CLI] Add stores verb app service entry points
[API] Add `/stores` to swagger spec
[API] Add `/stores` e2e tests
[API] Add `/stores` endpoint and handlers
[API] Add `/stores` domain logic
[API] Add `/stores` in mem repo
[API] Add `/stores` sqlite repo
[CLI] Connect store app service to API
```

> NOTE: If you do choose to use this approach, it is important to ensure
> the full test suite passes at each final merge commit (post-squash)
> after re-ordering.

#### Making titles easier to read during review

It's ok within a Pull Request to use other titles for squash commits to
make keeping track of development easier. As long as it is still clear
to the reviewer which commits will be squashed, and which are intended
to be merged as-is. Use the `squash` prefix without the `!` to make it
clear these need to be manually managed.

The following example shows a situation where due to the number of
changes required, the `--autosquash` format was avoided to make it
easier to understand:

```
[API] Add `/replica` endpoint to swagger spec
squash [API] Add tests for `/replica` endpoint
squash [API] Add endpoint and handlers
squash [API] Refactor replica repository interface
squash [API] Add domain logic
squash [API] Update in-mem repository implementation
squash [API] Add sqlite repository support
```

### Larger projects

On some occasions, such as for much larger pieces of work, we may adopt
one or more techniques to make the integration of complex work into
`main` more manageable.

Most strategies are a trade-off. Whichever approach is taken, the
proposed work process should be agreed by the team before work starts.
This ensures that system boundaries remain intact whilst work is under
way, and the division of work and general approach makes sense.


#### Merging inside-out

The inside-out approach can allow more frequent integration of work,
where feature toggles are either not available or add unnecessary
complexity. Rather than starting by merging end-to-end tests that
require the entire system to function - forcing the entirety of the work
to be in that one Pull Request - we break it down into discreet pieces
of work, that leave public boundaries intact at each stage.

End-to-end tests and other outer-layer acceptance tests can still be
written ahead of time, they are just kept in a separate development
branch until they are ready to be integrated.

This might mean that a specific Pull Request in isolation is missing
end-to-end tests, but this is OK if it has been properly coordinated.


#### Feature toggles/conditional compilation

Some situations may suit the use of feature toggles or conditional
compilation to allow code to be merged, but not be active. This is often
well suited to cases where the consumer of a component needs to control
feature visibility rather than just the internal development effort.


#### Feature branches

Significant work, particularly that requiring coordination between
multiple people working simultaneously, should be carried out on a
separate feature branch. This allows frequent integration of the main
codebase without requiring in-progress work to be merged into a release
branch.

Generally speaking one of the other above strategies for managing
individual units of work should still be applied, i.e. Pull Requests into
a feature branch should still be complete, logical units of work.

When merging a feature branch into a release branch, a great deal of
care should be taken as to how it is squashed into a sensible series of
final commits, that abide by the principals of release branch
development.

Feature branches should use the `feature/<issueNumber>-camelCaseName`
naming convention.


## See also

- [Pull Requests](PULL_REQUESTS.md).
- [Code Reviews](CODE_REVIEWS.md).


## Appendix - Code components

These components should be used in commit message titles:

- `Build` For `Makefile`, `CMake`, `setup.py`, etc. use by all builds.
- `CI` For work solely on GitHub Actions or similar deployments.
- `Core` For work within the core C++, non-interactive API.
- `Python` For work solely focused on the Python API.
- `UI` For commits related to the UI delegation system.
- `C` For work solely focused on the C API.
- `Docs` For work in the (distribution) Doxygen documentation or
  in-repository Markdown files.
- `Examples` For work included under the `examples` directory.
- `Lint` For miscellaneous changes that don't affect behavior, usually
  relating to linter fixes, `.gitignore` updates, etc.
- `PluginSystem` For work pertaining to the plugin system.
- `Tests` For work on test cases and test infrastructure.
- `Release` For commits bumping versions in preparation for a release.
