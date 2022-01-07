# OpenAssetIO Decision Records

This directory contains the records of key OpenAssetIO project decisions.
They cover the rationale and other options considered.

## Motivation

Any significant project decision should be recorded in a way that
encapsulates not only the outcome, but the reason for the change and any
alternatives proposed. This is essential to provide context post-fact,
should there ever be questions around the status quo.

## Process

1. New decisions should be opened as fresh PRs with the `decision
   record` label. Keeping DRs in their own PRs helps avoid coupling
   their life cycle with the code review churn of any given dev work.
2. Use comments as passive documentation to capture any discussions
   around the content or wording of the DR and the options it presents.
3. Push changes as new commits, including changes to `Status`.
4. Once the decision has been finalized, squash the commits and merge.

> Note: Comments made during the life cycle of the decision PR should be
> considered ephemeral. If salient points are raised, they should be
> reflected in the record itself prior to merge. If action items are
> added, open subsequent PRs to update the record as they are completed.

## Format

Records should be incrementally numbered based on their creation date
and use standard [GitHub Markdown](https://guides.github.com/features/mastering-markdown/)
using the template below. Copy should use US English spelling.

Each record should be stored in its own file, using the convention
`DR###-Kebab-case-title.md`.

### Template

```
# DR### Decision Title

- **Status:** Proposed|Decided
- **Impact:** Low|Medium|High
- **Driver:** @githubUsername
- **Approver:** @githubUsername
- **Contributors:** @githubUsernames [optional]
- **Informed:** @githubUsernames [optional]
- **Due date:** [optional]
- **Outcome:** High-level description of the change

## Background

Provide context on the decision to be made. Include links to relevant
research, or other related decisions, as well as information on
constraints or challenges that may impact the outcome.

## Relevant data

Add any data or feedback that the should be considered when finalizing
this decision.

## Options considered

### Option 1

Description

#### Pros

 - Pro 1

#### Cons

 - Con 1

### Option 2

Description

#### Pros

 - Pro 1

#### Cons

 - Con 1

Estimated cost: Small|Medium|Large

## Outcome

Summarize the outcome, stating which option was chosen and why.

## Action Items [optional]

 - [ ] Task @githubUsername
```
