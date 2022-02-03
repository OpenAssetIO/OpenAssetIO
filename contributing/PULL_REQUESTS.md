# Pull Request guidelines

PRs should aim to be small, containing a single meaningful change to
the project. For all merges, the target branch should be functional
after merge.
- For feature branches, or during alpha development, the target should
  be functional, but not necessarily feature-complete.
- For release branches the target should always be in a release-ready
  state before, and after any PR is merged.

For any significant change, it is common practice to break up changes
into several commits to ease understanding and review, and then
squash/rebase them together before merge. This ensures that the
long-term history contains commits with a workable granularity, without
the review process being overwhelming.

A good example of this is with TDD - having a commit that adds failing
tests, then one that makes them pass. Before merge, these two commits
will be squashed.

> Note: We always re-base to the `HEAD` of the target branch before
> merge.

The reason for this is to facilitate binary chops and ensure reverts on
any release branch are unambiguous. When rolling back a commit, there
should be no uncertainty as to which 'other' commits are needed to leave
the branch in a stable condition.


## What makes a good Pull Request?

There are several factors that make a Pull Request easy to review and
approve. Does it:

- Cover a small, complete, meaningful change.
- Describe the changes made, along with any notes for the reviewer eg:
  future work.
- Reference any relevant GitHub issues.
- Have a well-formed series of commits that encapsulate self-contained
  changes resulting in the desired functionality.
- Make use of `squash! <target commit title>` to indicate a commit that
  exists to ease review, that will be combined before the PR is merged.

**Important:** PRs to release branches will be rejected if they contain
any of the following:

- Incomplete functionality exposed through any public interface.
- Failing tests.
- Dead/commented/place-holder out code.
- Debug prints or other 'WIP' code.
- Notable deviation from the project coding standards.
- Redundant commits that implement something only to undo it later in
  the same PR.

For more information on preparing commits for a review, please see the
[commit guidelines](COMMITS.md).


## Our Pull Request process

Follow the steps below if you wish to open a merge-ready PR for review
(there are no strict requirements for a `WIP` PR):

1. Implement the functionality as defined by the Issue's acceptance
   criteria, and agreed design in a branch **on your own fork**.
2. Rebase and prepare your commits for review (see
   [commit guidelines](COMMITS.md)).
3. Push your branch to your fork.
4. Create a Pull Request to the target branch in the main repository.
5. Add the assigned Trusted Committers as reviewers. NOTE: Only add
   people who you _want_ to review the PR. PRs will only be merged when
   all added reviewers have approved.
6. Reviewers will comment using the `[question]`, `[consider]`,
   `[plan]`, `[fix]` severity ladder.
7. Respond to any review comments.
    - Any `[fix]` comments must be resolved before the PR can be merged.
    - Any `[question]` comments should be answered.
    - Any `[consider]` comments should be acted upon, or, a reason for
      not doing so added as a reply and the comment resolved.
    - Any `[plan]` comments directed at you need to be acted upon.
    - Use `fixup! <target commit>` commits to address specific comments.
    - Push your fixups. **do not rebase/force push unless specifically
      requested or need to wrangle a complex history**.
    - Reply to each review comment with a link to the relevant `fixup!`
      commit. **do not resolve the comment unless it is a rejected
      consideration**.
    - Re-request a review from relevant reviewers (using the button in
      the UI or @'ing them in a comment letting them know it's ready for
      a re-review).
8. Reviewers will resolve their comments once they are satisfied they
   have been addressed.
9. Once all comments are resolved, the last reviewer to review the PR
   will then either:
    - Request the commits be squashed _ready_ for merge.
    - Ask you to squash and merge yourself.
10. Squash the commits and force-push your branch.
11. Add a comment to the PR informing the reviewers it is ready for
    merge and re-request a review using the button in the UI, or, if
    originally requested by the last reviewer - merge into the target
    branch.

### WIP PRs

The `wip` label should be added to any PR that is not yet ready for
final review. You can use a WIP PR to ease sharing, discussion or for
an in-flight review. **A WIP labelled PR should _never_ be merged**.

When preparing  or evolving a WIP PR for review, it is absolutely fine
to force-push a new set of commits, based on the above guidelines over
the top of any existing work as long as it is coordinated with the
reviewer(s).
