# The contribution process

This project operates a Pull Request model, using the [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow)
approach. The rough outline is as follows:

0. Ensure there is a suitable [CLA](#contribution-sign-off) in place for
   you, or your organization
1. Chat with the Trusted Committers and community to define the scope of
   work
2. Fork the repo, and work in a branch
3. Create a Pull Request for Code Review
4. Address any comments
5. Work is merged

The main aim of the process is to keep people in the loop - avoiding any
surprises later on. This helps avoid churn/frustration for all involved.

## Defining the scope of work

The first stage defines a shared understanding of what work is to be
done, this should always be done in conjunction with the project's
Trusted Committers. The steps are:

1. Ensure you can describe the nature of your request or change, along
   with real-world use cases any why it is desirable.
2. Create a thread in the project [discussions](https://github.com/TheFoundryVisionmongers/OpenAssetIO/discussions/categories/ideas-and-change-proposals)
   area that describes the topic, this is to ensure:
    - There isn't any overlapping work already planned or in progress.
    - The change makes sense as part of any broader vision for the
      project.
    - There is agreement on next steps, which may include research
      and/or design phases.
3. Along with the trusted committers, create an issue using the
   What/Why/Acceptance Criteria outline that covers the definition of
   done for the work
4. Review the planned work with the team, and agree a testing strategy
   and target branch.
5. Trusted Committers will be assigned to review the work through to
   delivery.

## Development

We have a few golden rules for commits to release branches:

- All code should follow the project coding standards.
- `main` and maintenance branches should always be functional, once we
  pass alpha and beta, they must always be release ready.
- Commits should form meaningful atomic units of change. The build
  should never be (intentionally) broken between commits merged to
  release branches.
- Fix bugs in the oldest branch and merge forwards, do not cherry-pick
  back.
- All Pull Requests must be reviewed by someone who did not write the
  code.

### Working process

The process for feature development is as follows (we use the [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow) process):

1. Create a fork of the repository, and a working branch and begin work.
     - Keep the appropriate Trusted Committers in the loop with
       regarding any in-flight issues.
     - Request in-progress reviews if necessary to validate design
       choices by creating a [WIP PR](PULL_REQUESTS.md#wip-prs) and
       @-ing a Trusted Committer.
     - Branches should be named using the
       `work/<issueNumber>-<camelCaseTitle>` convention.
2. Upon completion, prepare your Pull Request in accordance with the
   [Pull Request guidelines](PULL_REQUESTS.md), for larger work, this
   may be targeted at a feature branch, rather than a release branch.
3. Address any feedback with `fixup!` commits, creating a separate
   commit for each comment thread.
4. Once approved, rebase and squash any `fixups!` or `squash!` commits
   authored as separate commits to ease review and re-request a review.
5. The Pull Request will be merged *by a reviewer* into the target
   branch.

> IMPORTANT: You should never merge your own PR unless instructed to by
> the reviewer.

### Coding standards

The mix of languages used in this project means there are some important
guidelines on how to format code and documentation written for the
project. These are outlined in the [coding standards](CODING_STANDARDS.md)
guide.

### Contribution sign off

OpenAssetIO is licensed under the [Apache 2.0 license](LICENSE). All
contributions to the project must abide by that license.

Contributions to OpenAssetIO require the use of the [Developer’s Certificate of Origin 1.1 (DCO)](https://developercertificate.org).
All commits must be signed-off as follows, before merge, to indicate
that the submitter accepts the DCO:

```
Signed-off-by: Jóna Jónsdóttir <jona.jonsdottir@example.com>
```

This can be added automatically to a commit using `git commit -s`.

We also require commits to be [GPG signed](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

In addition, contributors are required to complete either the Individual
or Corporate Contribution License Agreement. Please contact one of the
trusted committers for more information.

## Futher reading

- [Coding standards](CODING_STANDARDS.md)
- [Pull Requests](PULL_REQUESTS.md)
- [Commits and commit messages](COMMITS.md)
- [Code Reviews](CODE_REVIEWS.md)


## Trusted Committers

### Foundry
- @foundrytom [tom@foundry.com](mailto:tom@foundry.com)
- @feltech
