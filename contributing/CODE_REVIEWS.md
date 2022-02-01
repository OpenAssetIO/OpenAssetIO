# Code Review guidelines

Code Reviews are an essential part of the development cycle. We involve
reviewers early on in the development process, and ensure everyone is on
the same page and on board with the approach before implementation
starts (see the [development process guide](PROCESS.md) for more
details).

This document provides some guidelines for a **reviewer** when
approaching the final implementation required before code is merged into
a release branch.

If you are a **contributor**, the [Pull Request guide](PULL_REQUESTS.md)
has some helpful tips of how to prep for a code review.


## The purpose of a code review

We require a code review for several reasons, mainly this is to check:

- The code functions as expected and meets the agreed Acceptance
  Criteria (ACs).
- The code is easily understood by a fresh pair of eyes.
- The code fits the conventions and design patterns used by the project.

There are additional benefits to code reviews, and we encourage all
project maintainers to take an active interest in all Merge Requests
that are made, even if they are not directly requested to review the
work.

- It helps broaden the reader's understanding of areas of the project
  they may not be familiar with.
- The discussions around a review can help understand broader topics
  such as best practices, design patterns and idiomatic programming.
- Someone totally distanced from the work may spot things those 'deep in
  the weeds' miss.


## Review priorities

When reviewing a Pull Request, there are many things to be considered.
Some are more important than others. The guidelines below aim to
illustrate the relative priorities of different things you may be
considering.

1. Is CI passing?
2. Does a build of the code do what's required by the Acceptance
   Criteria, before even looking at the implementation?
3. Does the implementation fit the agreed approach, if not, is this of
   any concern?
4. Is there sufficient test coverage?
5. Is the code understandable and suitably documented such that it can
   be understood with no further questions?
6. Does the final proposed series of commits (once squashed as
   illustrated) function correctly at each step? In particular, the
   build should not be broken and all public interfaces (API or UI)
   should work.
7. Has the documentation been updated?
8. Does it follow the design patterns adopted by the project for similar
   functionality?
9. Does it follow the project coding standards?
10. Do commit messages follow the template and contain enough rationale?


### Suggested approach

1. Grab the branch (or a CI build artifact if available), test
   functionality against the Acceptance Criteria defined for the work.
2. Check implementation against the above priorities.


## Making comments

As part of a review, you will most likely need to make comments. We
have adopted a "feedback ladder" methodology to help avoid ambiguity
about what needs to happen to resolve the comment, and merge the code.

The idea is that any comment you make should be prefixed with a severity
label. We have four main labels that should be used. They describe the
action that the contributor needs to take for the comment to be
resolved. Labels should be the first thing in the comment and formatted
as follows:

- `[fix]` Something that must be addressed before merge.
- `[plan] @github.username <thing to do>` Something that must be
  addressed, but does not block a merge. These comments need to explicit
  state who needs to do what. That person needs to have done the action
  before the comment can be resolved. Examples of actions may include
  "Create an Issue..." or "Organize a meeting to discuss..."
- `[consider]` Something that is not required for merge but should be
  considered. The contributor should affect that change, or, reply with
  a reason for not doing it and resolve the comment. Considerations can
  also use a secondary label such as `[nit-pick]` or `[minor]` to weight
  the importance of the consideration.
- `[question]` Something that needs clarifying before an action can be
  determined.


## Verifying amendments

The contributor will act upon comments, and re-request a review from
you. Once they have done this, take a look through your comments
resolving all the ones you are satisfied with, or adding a reply if
anything is a miss.

The Pull Request can't be merged until all of your comments are
resolved.

> Note: If you are unable to resolve the comment directly (as it
> requires repository write access), then add a `:thumbsup:` (👍)
> reaction to the thread to indicate that it can be resolved by the
> committer.


## Concluding the review

If you have no further comments to make (or have resolved your final
comment after the contributor has updated the code), you can approve the
Pull Request.

If you are the _last_ reviewer you then have a few options:

 1. If there are `fixup!` or `squash!` commits, either:
   - Request the contributor to squash _ready_ for merge and final
     approval. They will the re-request a review.
   - Tell the contributor to squash and merge at their convenience.
 2. If all commits are merge-able (either it's a simple PR, or the above
    step has already been done), merge the PR yourself.

> NOTE: The last reviewer needs to do one of the above things - or the
> PR will never be merged! Committers are not allowed to merge their own
> PRs unless instructed by another maintainer.


## Draft/Work in progress code reviews

On occasion, contributors may request reviews of work in progress to
avoid any significant changes further down the line. In these situations
the review should first focus on any specific areas the contributor
wishes to be considered. There may be many loose ends or incomplete
work, so check first if something you spot is "ready for public
attention yet".

It is always still worth raising anything you notice that would come up
again in a final code review. Discussing it early helps to prevent
wasted work down the line.


## See also

- [Pull Requests](PULL_REQUESTS.md)
- [Commits](COMMITS.md)
