# DR016 One-to-many result paging

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @feltech
- **Approver:** @elliotcmorris @foundrytom
- **Contributors:** @feltech @elliotcmorris @foundrytom @mattdaw
- **Informed:** @mattdaw
- **Outcome:** Split batching from paging and page using a cursor object

## Background

The OpenAssetIO API contains functions that can return an arbitrarily
long list of results.  In particular, the current core API has functions
for retrieving a list of versions of a given entity, and retrieving a
list of entities that are "related to" another entity in some way.

Taking the related entities query as an example: this could be sibling
or parent-child relationships (e.g. shot and sequence), or more loose
relationships (e.g. the project file that was executed to generate a
render).

The current API design provides the host with a list of entity
references that correspond to an input entity-relationship pair.

There may be multiple entity-relationship pairs provided as input to
a single API call, allowing the manager plugin to leverage batching
optimizations. Note that, typically, batching primarily addresses
network latency concerns, in addition to database query optimizations.

In the most general case, the host cannot know the size of the list of
related entity references that will be returned to it. This clearly
poses a scalability issue.

Database and web APIs have had to deal with this problem for decades,
and invariably provide some mechanism of returning slices of result sets
or "pages" that can be iterated through, lazily fetching chunks of data
in a controlled way.

In an ideal situation, requesting subsequent pages has performance
benefits over repeating the same query twice (or more) with different
range arguments, and yet work is performed lazily as pages are requested
so that no unnecessary processing of unused pages is performed.  Also,
pages should be stable, in that results are not skipped nor appear more
than once on successive pages.

Ultimately, the implementation must be provided by the manager plugin
authors. The mechanism chosen in this DR can only present an abstract
interface that the plugin must satisfy. As a result, characteristics
such as page stability and performance cannot be guaranteed, and nor
do we desire to place such restrictions upon the implementation. However
we can at least ensure that the chosen mechanism does not preclude such
optimisations.

The mechanism of paging tends to take three broad forms

- (Integer) offsetting
- (Opaque) page tokens
- Cursor objects / iterators

The addition of a paging mechanism to the batched query API raises a
number of questions around host and plugin implementation complexity.

## Relevant data

A (certainly non-exhaustive) selection of API design guides and
implementations for the paging strategies outlined above can be found in
the following links.

* A broad discussion of paging strategies:
  - [Patterns for API Design](https://microservice-api-patterns.org/patterns/quality/dataTransferParsimony/Pagination)
* Offset based designs:
  - [Atlassian](https://developer.atlassian.com/server/framework/atlassian-sdk/atlassian-rest-api-design-guidelines-version-1/#standard-query-parameters-in-uris)
  - [Australian Government](https://apiguide.readthedocs.io/en/latest/build_and_publish/batching_results.html)
  - [Microsoft](https://github.com/Microsoft/api-guidelines/blob/master/Guidelines.md#982-client-driven-paging)
* Page token based designs:
  - [Google Cloud guidelines](https://cloud.google.com/apis/design/design_patterns#list_pagination)
  - [Google Cloud Datastore](https://cloud.google.com/datastore/docs/concepts/queries#datastore-datastore-cursor-paging-python)
  - [Twitter](https://developer.twitter.com/en/docs/twitter-api/pagination)
  - [Slack](https://slack.engineering/evolving-api-pagination-at-slack/)
* Cursor object designs:
  - [Cisco](https://github.com/CiscoDevNet/api-design-guide#363-get)
  - [Cloudfoundry](https://github.com/cloudfoundry/cc-api-v3-style-guide#pagination)
  - [JDBC](https://docs.oracle.com/javase/8/docs/api/java/sql/ResultSet.html)
  - [MongoDB](https://www.mongodb.com/docs/manual/reference/method/js-cursor/)
  - [Python PEP 239 DB-API](https://peps.python.org/pep-0249/#fetchmany)
    used by many database libraries.
  - [Ruby on Rails](https://api.rubyonrails.org/v7.0.4.2/classes/ActiveRecord/Batches.html#method-i-find_in_batches)
  - [W3C IndexedDB Cursor API spec](https://w3c.github.io/IndexedDB/#idbcursor)


## Options considered

### Paging option 1 - Offseting

Host provides an integer offset argument to locate the start of the next
page, and a limit argument providing the page size.

#### Pros

- Conceptually simple for the host.
- Jumping arbitrarily to nth page is trivial.
- Transactions, indexing and caching technologies exist that can
  alleviate stability and performance problems, to some extent.

#### Cons

- Anomalous page results if insertions/deletions can happen before next
  page is retrieved, or if ordering is not stable.
- Server cannot negotiate page size - there is no mechanism to signal
  that more results are available other than by exhausting the page
  limit.
- Poor performance on the back-end for large offsets into non-trivial
  (i.e. non-indexed/cached) queries, where many rows must be iterated
  through and skipped over.
- No mechanism to inform the manager that no further pages are required.

### Paging option 2 - Page token

Page tokens (also often called "cursors") allow the server to retain
control over where to find the next page (typically they are a pointer
to an element in the overall result list), alleviating stability
problems.

Each query returns a page token as well as a page of results. The
original query is repeated to retrieve subsequent pages, but with an
updated page token provided by the previous query.

#### Pros

- Conceptually simple.
- Matches the most common pattern of pageable HTTP APIs allowing e.g.
  the page token to be a thin wrapper around a "real" page token(s).
- Manager plugin can remain conceptually stateless, since required state
  is bundled up in the page token.
- Page token is (or can be) immutable, aiding thread-safety.
- Using the page token to determine if more pages are available (e.g.
  a `None` token means exhausted) allows the server to override the
  page size, opening up an avenue for optimisation.
- Destruction hooks on a page token (e.g. destructor of a class-based
  token) could signal to the manager that the page is no longer
  required, allowing e.g. cache cleanup.

#### Cons

- Adding more functionality (e.g. previous page) requires additional
  sibling functions or arguments.
- Adding metadata (e.g. total results) requires additional sibling
  functions or arguments.
- Function invocations to fetch subsequent pages must pass all the same
  arguments, such that they are valid for the page token. This is
  error-prone and/or redundant.

### Paging option 3 - Cursor objects / iterators

Cursor objects are an abstraction over some unknown internal paging
mechanism, which may be a page-token, or some other mechanism.
This cursor could be an object-oriented wrapper with methods, e.g.
`.next()`, or a data structure with opaque links, e.g. containing a URL
to the "next" page.

For example, a simple paging cursor object may look like:
```python
class AbstractCursor:

    def getPage(self, pageSize: int) -> List[EntityReference]:
        # Get next page of refs.
        ...

    def skip(self, pageSize: int):
        # Skip over records without fetching.
        ...

    def remaining(self) -> Union[int, None]:
        # None means "unsupported".
        ...
```

#### Pros

- Retrieving the data can be decoupled from traversal of pages, allowing
  for lazy network retrieval of desired pages.
- Additional metadata can be included in the cursor (e.g. remaining
  pages) in an extensible way.
- A mutable, stateful cursor object maximizes opportunities for the
  manager plugin to optimize query caches.
- Destruction of a cursor object could be used as a signal to the
  manager that no further pages are required, allowing e.g. cache
  cleanup.

#### Cons

- Manager plugin must implement yet another interface.
- Complexity of binding to multiple target languages.
- A mutable, stateful cursor violates the stateless design principle of
  interactions with manager plugins. This causes complications, e.g.
  thread-safety.
- An immutable cursor object (such that `.next()` returns a new cursor
  object), could increase optimisation complexity for the manager
  implementation, e.g. managing query cache sharing, lifetime and
  updates across multiple "live" cursors.
- The temptation to directly wrap a "real" DB cursor object in our
  (potentially long-lived) paging cursor object could lead to connection
  pool starvation.

### Paging option outcome

The pros and cons considered are insufficient to decide on a final
design.  However, we can at least rule out any offset-based solution,
given the lack of flexibility afforded to the manager's implementation,
resulting in poor stability and likely manager overhead of record
counting.

More factors will be considered in the following sections, taking into
account only page token and cursor object based solutions.

## Considering batching

Additional considerations arise when considering how batching can be
handled algongside paging. There are three broad strategies

- Split batching from paging, using a different API method for each.
- Page through the results from all the batched input elements in
  lockstep, i.e. whole-batch paging.
- Page through the results of each batched input element independently,
  using individual sub-queries within the whole-batch query, i.e.
  per-element paging.

Each of these batched paging designs combines more or less well with the
various paging options presented above.

The above strategies are thus considered in the following sections with
respect to page token and cursor object designs.

### Batched paging option 1 - Split batching from paging

E.g. Non-paged batch signature
```python
# Callback taking index of batch element and all results for that element.
SuccessCallback = Callable[[int, List[EntityReference]], None]

def relatedEntities(
    batch: List[EntityReference], relationship,
    successCb: SuccessCallback, errorCb): ...
```

E.g. Page token paged signature

```python
def relatedEntities(
    input: EntityReference, relationship, limit=-1, pageToken=None
) -> Tuple[AbstractPageToken, List[EntityReference]]: ...
```

E.g. Cursor object paged signature
```python
class AbstractCursor:
    def getPage(self, pageSize: int) -> List[EntityReference]:
        ...
    def skip(self, pageSize: int):
        ...

def relatedEntities(
    input: EntityReference, relationship) -> AbstractCursor: ...
```

#### Pros

- Simple direct interface for the host application.
- Simpler for manager plugin implementors to reason about (as evidenced
  by ad-hoc discussions with collaborators).
- Hosts should usually have a good idea whether batching or paging is
  more appropriate for the query they are making.
- Manager and host do not need to consider both paging and batching at
  the same time, which is a complex convergence of concepts.
- Manager implementation can typically be a lightweight wrapper around
  common HTTP/DB API pagination patterns.

#### Cons

- Precludes batching optimisations by the manager when paging is
  required.
- Requires implementation of two methods by the manager: one for
  batched, one for paged.
- Potential difficulty for some hosts/queries to determine a priori
  which API (paging or batch) is the most optimal choice.
- Having the choice adds a foot-gun for host developers to shoot
  themselves with by accident.
- Precludes hosts atomically expressing more complex queries that may
  be required by spreadsheet-type UIs.

### Batched paging option 2 - Whole-batch paging

E.g. Page token

```python
# Callback taking index of batch element and selected page of results.
SuccessCallback = Callable[[int, List[EntityReference]], None]

def relatedEntities(
    batch: List[EntityReference], relationship,
    successCb: SuccessCallback, errorCb,
    limit=-1, pageToken=None
) -> AbstractPageToken: ...
```

E.g. Cursor object

```python
class AbstractCursor:
    def getPage(self, pageSize: int) -> List[List[EntityReference]]:
        ...
    def skip(self, pageSize: int):
        ...

def relatedEntities(
    batch: List[EntityReference], relationship) -> AbstractCursor: ...
```

#### Pros

- Whole batch is paged at once, retaining batch-awareness in the
  manager for subsequent pages.
- Conceptually simpler API for both host and manager if only a single
  page is active across the whole batch.

#### Pros (page token specific)

- Per-element callback means it's trivial to skip processing elements of
  the input batch whose pages are exhausted.
- Retains existing design in line with OpenAssetIO design principles,
  i.e. non-paged signature is simply the same function but ignoring
  optional arguments.

#### Cons

- Batch elements cannot enter an error state in isolation, since paging
  is whole-batch. E.g. cursor objects may raise an exception, but that
  would preclude getting pages for non-failing elements; and page tokens
  may fail independently, but then _some_ token must still be passed
  into the next call, and it is not clear how that should work.
- Collaborators working on manager plugins raised this as being
  particularly tricky to implement.
- Likely that the manager plugin must combine multiple back-end page
  tokens into one, adding complexity to ensure they are maintained in
  sync.

#### Cons (cursor object specific)

- Additional metadata in the object is limited to whole-batch data.
- Wasted processing of empty lists by the host when pages are exhausted
  i.e. when there are still pages remaining for some inputs but not
  others.

### Batched paging option 3 - Per-element paging

E.g. Page token

```python
# Callback taking index of batch element and selected page of results.
SuccessCallback = Callable[[int, List[EntityReference]], None]

def relatedEntities(
    batch: List[EntityReference],
    relationship,
    successCb: SuccessCallback,
    errorCb,
    limit: -1,
    pageTokens: List[AbstractPageToken]
): -> List[AbstractPageToken]: ...
```

E.g. Cursor object

```python
class AbstractCursor:
    def getPage(self, pageSize: int) -> List[EntityReference]:
        ...
    def skip(self, pageSize: int):
        ...

# Callback taking index of batch element and cursor object.
SuccessCallback = Callable[[int, AbstractCursor], None]

def relatedEntities(
    batch: List[EntityReference],
    relationship,
    successCb: SuccessCallback,
    errorCb): ...
```

#### Pros

- Manager is under no obligation to consider errors in other batch
  elements when implementing query behaviour, as pagination method need
  not be synchronized.

#### Pros (cursor object specific)

- Individual cursors can be incremented independently, potentially
  reducing wasted queries.

#### Cons

- Batching is very difficult to optimize for the manager, especially
  after the first page.
- Batch-optimized queries have unpredictable performance profile for
  the host, given the wide range of potential implementations.

#### Cons (cursor object specific)

- Cannot advance to the next page as a batch operation.

### Batched paging option outcome

Given the reported difficulty of crafting queries that are both batch
and paging-aware, we opt to go with Option 1 and split the paging API(s)
from the batched API(s).

This then leaves only a batch-only signature, plus a decision between
two remaining paging solutions: (non-batched) page token or cursor
objects.

## Outcome

We opt for a non-batched cursor object design.

Avoiding conflating batching and pagination simplifies manager plugin
implementations.

Whilst we may miss out on some theoretical performance, we have been
unable to find any real-world examples showing this sort of batched-page
optimization.

A cursor object maximises future extensibility, where new functionality
can be added without further polluting the `Manager`/`ManagerInterface`
class. They also naturally capture arbitrary state that the manager
may wish to store as part of the ongoing query.

A cursor object also encapsulates the arguments required for requesting
subsequent pages, whereas a page token requires (potentially
redundantly) re-specifying the same arguments for each subsequent page
along with the page token. This could be mitigated for the page token
design by having a separate API for page token operations, but this
starts to closely resemble a cursor object solution (with the `this`
pointer fed from outside).

Cursor objects also reflect the most common programmatic approach to
paging through the results of a database query, presenting a familiar
interface for plugin authors, and mapping well to common back-end SDKs.

The additional complexity of the interface compared to a page token
solution, for plugin authors, host authors and future language bindings,
is small compared to the advantages in extensibility. For example, we do
not foresee any issues in following the existing pattern of the
(prototype) C API.

Enforcing excessively stateful or complex functionality on the cursor
object, e.g. by mandating `skip` or `remaining` methods, as used in the
sketched examples, is a cause for concern. We do not propose to mandate
such methods. Methods may be added, but most if not all will be optional
such that the host will have to test the capabilities of the cursor
object before using them.

## Appendix: Considering manager implementations

The following subsections sketch some possible implementations of
manager-side queries for the remaining options under consideration. They
are not to be considered canonical.

### Using Python's DB-API standard

Python's [PEP 239 DB-API](https://peps.python.org/pep-0249/#fetchmany)
standard provides a canonical example of an API for interacting with a
back-end SQL-like database.

#### Page token signature

The page token design, as envisioned in earlier sketches, is further
elaborated below, as a possible manager implementation using DB-API.

```python
class PageToken(AbstractPageToken):
    def __init__(self, cursor):
        self.cursor = cursor


def relatedEntities(
    input: EntityReference, relationship, limit=-1, pageToken=None
) -> Tuple[AbstractPageToken, List[EntityReference]]:

    if pageToken is None:
        my_relationship_type: str = get_my_relationship_type(relationship)

        cursor = get_my_connection().cursor()
        cursor.execute(
            f"""
            SELECT ToRef FROM Relationship
            WHERE RelationshipType = ?
            AND FromRef = ?
            """, my_relationship_type, str(input))

        pageToken = PageToken(cursor)

    if limit <= 0:
        result_set = pageToken.cursor.fetchall()
    else:
        result_set = pageToken.cursor.fetchmany(limit)

    related_refs = [EntityReference(result[0]) for result in result_set]
    return pageToken, related_refs
```

#### Page token alternative - command pattern

One of the major Cons of page tokens as sketched so far is that the
original query arguments must be redundantly re-specified when fetching
subsequent pages. To overcome this we can split the construction of page
tokens from the operations performed on them.

This could be done as a series of methods, however that then looks
extremely similar to a cursor object design.

Instead, the sketch below takes a command pattern approach. We add a
single new method, with the operation to perform given as an additional
argument.

```python
def relatedEntities(
        input: EntityReference, relationship) -> AbstractPageToken:

    my_relationship_type: str = get_my_relationship_type(relationship)

    cursor = get_my_connection().cursor()
    cursor.execute(
        f"""
        SELECT ToRef FROM Relationship
        WHERE RelationshipType = ?
        AND FromRef = ?
        """, my_relationship_type, str(input))


def relatedEntitiesPageCmd(
    pageToken, command="next", limit=-1
) ->  Tuple[AbstractPageToken, List[EntityReference]]:

    if command == "next":
        if limit <= 0:
            result_set = pageToken.cursor.fetchall()
        else:
            result_set = pageToken.cursor.fetchmany(limit)

        related_refs = [EntityReference(result[0]) for result in result_set]

        return pageToken, related_refs
    else:
        raise NotImplementedError()
```

#### Cursor object signature

The following sketch wraps a DB-API cursor in an `AbstractCursor`,
showing a straightforward mapping of functionality, and demonstrating
the extensibility to support other common cursor API methods (in this
case, skipping over records without the cost of fetching all the
results).

```python
class Cursor(AbstractCursor):
    def __init__(self, cursor):
        self.__cursor = cursor

    def getPage(self, pageSize) -> List[EntityReference]:
        result_set = self.__cursor.fetchmany(pageSize)
        return [
            EntityReference(result) for result[0] in result_set]

    def skip(self, pageSize):
        self.__cursor.scroll(pageSize)


def relatedEntities(
        input: EntityReference, relationship) -> AbstractCursor:
    my_relationship_type: str = get_my_relationship_type(relationship)

    cursor = get_my_connection().cursor()
    cursor.execute(
        f"""
        SELECT ToRef FROM Relationship
        WHERE RelationshipType = ?
        AND FromRef = ?
        """, my_relationship_type, str(input))

    return Cursor(cursor)
```

### Using a REST API

The following sketches investigate an alternative back-end
implementation, namely that of a hypothetical REST API.

The proposed relationship query REST endpoint interpolates the entity ID
and relationship type in the path, and optionally supports a limit and
page token query parameter(s).

In response to a relationship query the API returns a JSON object with a
`"data"` field, containing the list of related entity references, as
well as some other metadata fields, including a `"next_page_token"`
string, to be used in a subsequent REST API request to fetch the next
page.

#### Page token signature

A REST API lends itself nicely to a page token based solution, with the
page token object being a simple wrapper around the string token
returned by the API.

```python
class PageToken(AbstractPageToken):
    def __init__(self, token):
        self.token = token


def relatedEntities(
    input: EntityReference, relationship, limit=-1, pageToken=None
) -> Tuple[AbstractPageToken, List[EntityReference]]:

    my_relationship_type: str = get_my_relationship_type(relationship)
    my_entity_id: str = get_my_entity_id(input)

    endpoint = f"https://api.example.com/entity/{my_entity_id}/related/{my_relationship_type}?"

    if limit > 0:
        endpoint = endpoint + f"limit={limit}&"
    if pageToken is not None:
        endpoint = endpoint + f"page_token={pageToken.token}"

    response = requests.get(endpoint).json()

    related_refs = [EntityReference(elem) for elem in response["data"]]
    next_page_token = PageToken(response["next_page_token"])
    return next_page_token, related_refs
```

#### Cursor object signature

Adapting a REST API to wrap in a cursor object is fairly trivial.

Note, however, that the additional `skip` functionality is implemented
in a brute-force way - retrieving results and throwing them away. It's
possible a REST API would have a native "skip" endpoint, but rare.

```python
class Cursor(AbstractCursor):
    def __init__(self, entity_id: str, relationship_type: str):
        self.__entity_id = entity_id
        self.__relationship_type = relationship_type
        self.__token = None

    def getPage(self, pageSize) -> List[EntityReference]:
        endpoint = f"https://api.example.com/entity/{self.__entity_id}/related/{self.__relationship_type}?"
        if pageSize > 0:
            endpoint = endpoint + f"limit={pageSize}&"
        if self.__token is not None:
            endpoint = endpoint + f"page_token={self.__token}"

        response = requests.get(endpoint).json()

        self.__token = response["next_page_token"]

        return [EntityReference(elem) for elem in response["data"]]

    def skip(self, pageSize):
        endpoint = f"https://api.example.com/entity/{self.__entity_id}/related/{self.__relationship_type}?"
        endpoint = endpoint + f"limit={pageSize}&"
        if self.__token is not None:
            endpoint = endpoint + f"page_token={self.__token}"

        response = requests.get(endpoint).json()

        self.__token = response["next_page_token"]


def relatedEntities(
        input: EntityReference, relationship) -> AbstractCursor:

    entity_id: str = get_my_entity_id(input)
    relationship_type: str = get_my_relationship_type(relationship)

    return Cursor(entity_id, relationship_type)
```
