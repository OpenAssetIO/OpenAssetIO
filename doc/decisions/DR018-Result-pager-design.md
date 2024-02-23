# DR018 Result pager design

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @foundrytom @feltech @elliotcmorris
- **Approver:** @feltech @elliotcmorris
- **Outcome:** Result set pagers will facilitate a general "moving
  window" approach vs a simple one-shot queue.

## Background

Certain OpenAssetIO API methods can produce large sets of data.
[DR016](DR016-One-to-many-result-paging.md) covers the evolution in
thinking that lead us to expose this data through a lazy "result pager".

These pagers are supplied by the relevant `Manager` methods. The caller
then interacts directly with the pager to retrieve a sub-set of the
data, _n_ results at a time.

During the design of the pager API, it quickly became apparent that
there were two possible ways think about the role of the pager.

This DR describes these two high-level conceptual models, and which
should be used when evolving the pager interface in the future.

## Relevant data

- [DR016](DR016-One-to-many-result-paging.md) opted for the pager
  solution partly as it facilitates future extensions to data set
  navigation with minimal disruption to the rest of the API.

- By preference, OpenAssetIO opts for delegation over generalization -
  to try and avoid the "lowest common denominator" trap awaiting
  anyone who attempts to generalize the interactions between complex
  systems.

- Delegation also aims to encourage consistency across tools as
  interactions with the manager are then presented via its native UI.

## Options considered

### Option 1 - "Simple queue"

The pager is a marshal manning a simple queue. There is a large a number
of results, and they are supplied to the caller a page at a time. Once
`next` has been called, there is no way to retrieve the data for that
page again, without repeating the initial `Manager` method call and
obtaining a new pager.

Its interface could look like this:

```python
class Pager:

    def next() -> [Value]
        """
        Retrieves the next page of results.
        """

    def hasMore() -> Bool
        """
        Determines if calls to `next` will yield more results.
        """
```

It is assumed that UI delegation would be used for any more advanced
interactions.

#### Pros

- Simple, well understood data access pattern. Implementations are
  guaranteed that the first page is always accessed.
- Smaller surface area makes it easier to support across a variety of
  back end implementations.
- Discourages direct use of the API for complex workflows, encouraging
  delegated UX, which can result in a more consistent user experience.

#### Cons

- Accessing data from anything other than the first page requires
  traversal of all preceding pages.
- Not all runtime environments support delegated UX and/or have critical
  mass such that a manager would provide them with suitable UI
  components.
- Limiting to a simple queue potentially offsets some argued benefits of
  a pager object in terms of future extension, and could even be said to
  be more concisely expressed as an additional token supplied to the
  main `ManagerInterface` method.

### Option 2 - "Moving window"

The pager is a moving window into the results, facilitating more
general navigation of the data set.

Its interface could look like this:

```python
class Pager:

    def get() -> [Value]
        """
        Retrieves the results for the current page.
        """

    def next() -> None
        """
        Advances the pager to the next page.
        """

    def previous() -> None
        """
        Rewinds the pager to the previous page.
        """

    def hasNext() -> Bool
        """
        Determines if there are results after the currrent page.
        """

    def hasPrevious() -> Bool
        """
        Determines if there are results before the currrent page.
        """
```

#### Pros

- Facilitates more complex uses of the underlying data beyond gated
  consumption of a fixed stream.
- Allows runtimes without delegated UX support to build more advanced
  workflows.
- Extendable to more complex traversal concepts such as jumps and
  skips should the need for them arise.

#### Cons

- Larger surface area to map to specific back-end implementations, where
  not all concepts may be supported.
- Less predictable data access patterns as the consumer is free to use
  the pager however it wishes.
- Discourages UX delegation, which may lead to an inconsistent user
  experience.

## Outcome

We opt to think of pagers as "moving windows", to avoid artificially
limiting scenarios where OpenAssetIO may be well suited to exchanging
data. To avoid onerous implementation requirements, we will restrict the
initial pager API to the minimum required to support known workflows.

### Rationale

OpenAssetIO is meant to more generally support interactions between
tools and data management systems. Focusing too heavily on UI delegation
may preclude its use in many scenarios, given the variety of languages
and tech stacks in use.
