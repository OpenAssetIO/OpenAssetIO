# DR016 Hinting batch failure strategy

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @fdonal
- **Approver:** @foundrytom @feltech @ecmorris @fdonal
- **Outcome:** A new Context property will be used to hint that a batch
  may be aborted in the event of an error for a single element.

## Background

OpenAssetIO is a batch-first API. Presently the manager is required to
provide a result for each element of the batch - the data, or an error.

Results are provided by an element-wise callback mechanism, regardless
of how data is retrieved internally.

There are many scenarios in which a host may treat a failure for any
element in the batch as a failure of the whole request. For example,
when determining the inputs to a render.

Requiring the manager to continue to process remaining elements can
result in significant redundant work to being performed, potentially
impacting service availability.

At scale, hinting to the manager that a batch is permitted to "fail
fast" provides the opportunity to reduce pressure on back-end systems.

This failure mode can not be assumed, as the inverse scenario where
individual element failures are expected also exist. When querying the
availability of an entity in different scopes, for example.

As the behavour is determined by the host, we need a mechanism to
express the desired operational mode as part of an API request.

## Relevant data

> The scenario I have in mind is a resolver daemon that's implemented as
> a shared-nothing cluster of processes that each cache positive
> lookups... cache misses result in a query against a canonical
> database.
>
> If I send a render to the farm and 500 Nuke processes start
> up concurrently and each send a batch request of 1000 URIs to the
> resolver daemon, it might be useful to say - if you fail to resolve a
> URI, don't bother with the others because either
>
> - I already know they'll fail too.
> - I can't do useful work unless I get 100% of my resolves back.
>
> Alternatively my Nuke render might DDOS my database, because we'll get
> 500 * 1000 resolves hitting it concurrently. Admittedly those numbers
> would have to be higher to be truly worrying but renderfarms gonna
> renderfarm. It's the kind of thing that might happen when you send a
> job to the wrong datacenter and your render says "give me paths local
> to this datacenter for these 1000 assets" and they haven't been synced
> there yet.

- All OpenAssetIO requests are stateless, and parameterised with all the
  data required to service the request. This includes a description of
  the calling environment via the `Context` object. The Context contains
  fields that describe the nature of the hosts intent, including access
  (read or write) and the lifetime of query responses (transient,
  persisted, etc).

- The manager must consider the host intent defined by the Context and
  adjust its behaviour accordingly (e.g. erroring write access to a
  read-only entity)

- The manager is not required to order the result callbacks in the same
  order as the input data. Only that a callback must be made for each
  element before the method returns.

- The `openassetio.test.manager` harness provides an
  `apiComplianceSuite` test framework that helps plugin developers
  ensure that they fulfill the API contract, and its edge cases.

## Options considered

### Option 1 - No change

Do nothing, as it's not a significant enough concern.

#### Pros

- Avoids variable behaviour of API methods.
- One less thing for a manager to consider during implementation.

#### Cons

- See the illustrative scenario in the section above.
- Real-world managers may not be able to batch API operations, resulting
  in significant practical impact of its absence.

### Option 2 - Add parameter

Add parameter to relevant methods `bool abortOnBatchElementError`.
See the appendix for a description of its effect.

#### Pros

- Plainly visible, making it clear it is part of the API contract.

#### Cons

- The args list becomes even longer.
- A different mechanism to the other 'host behaviour' descriptors in the
  Context.

### Option 3 - Extend Context

Add a new field to the Context struct `bool abortOnBatchElementError`.
See the appendix for a description of its effect.

#### Pros

- Coherent with the other Context fields that affect manager behaviour.

#### Cons

- As with other context fields, it is not immediately obvious that a
  Manager should consider it.

## Outcome

We will adopt Option 3, and extend the `apiComplianceSuite` to ensure
that manger implementations correctly satisfy the resulting API
contract.

## Appendix - `abortOnBatchElementError`

When `true`, the manager should abort at the first element error.

However, any given manager implementation may, or may not be able to
batch queries to its back-end. The batch size to the back end may also
not match the request batch size. The upshot of this is that when an
element error is encountered, _there may already be additional sucessful
elements already processed_.

For reasons of flexibility and performance, The manager is not required
to call callbacks in element order.

So what does 'abort' mean in terms of callbacks? The abort mechanism is
entirely motivated by peformance and the reduction of redundant work.
So, we define the required manager behaviour as:

- For **read** operations, no more callbacks should be made after the
  first element error is encountered, regardless of any other available
  success elements that have not yet had their callback invoked. This
  ensures that a minimum number of callbacks are made. And provides the
  simplest code path for the manager's implementation.

- For **write** operations, all successfully processed elements should
  have their callback invoked before the first error element callback is
  made. After this, no further callbacks should be made. This attempts
  to minimize the possibility of dangling handles for new entities[^1],
  whilst still avoiding unnecessary work in the back-end. We believe
  this concern justifies the additional callback ordering overhead in
  the manager's implementation.

[^1]: Note that a proper transaction mechanism is scheduled for future
addition to the API.
