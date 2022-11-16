# DR009 Batch method result types for `ManagerInterface`

- **Status:** Decided
- **Impact:** High
- **Driver:** @feltech
- **Approver:** @foundrytom @feltech
- **Contributors:** @foundrytom @feltech
- **Outcome:** Batch methods will adopt a per-result callback mechanism.

## Background

OpenAssetIO employs a batch-first design. In that, all data centric
methods take multiple inputs, and produce multiple outputs. This allows
a `PythonPluginSystemManagerPlugin` to optimize queries to potentially
high-latency back-end services.

Many methods may have per-value error states, such that the output of
these methods is never of a uniform type. For example, `resolve` for any
given entity reference may provide a `TraitsData` instance, or an error.
An error for a specific value should not error the entire batch.

This raises the question of how to best express the resulting data
across the variety of languages supported by OpenAssetIO.

## Relevant data

OpenAssetIO core is currently exposed through C, C++ and Python. The C
API serves as a binding point for other languages.

A design mantra is that the implementation in any given language should
be as idiomatic as possible. An exception to which is that Python and
C++ are often used in the same breath within M&E DCC applications,
keeping those two languages as close to each other as possible has many
benefits.

The performance of API methods is important, as many scenarios
(particularly `resolve`) have a high query volume. Syntax alone is not
enough of a justification for any particular design choice.

For the scope of this document, it is assumed that the input to any of
these methods will be an array, regardless of the choices here.

Input options are not explored here, as the sole purpose of the
batch-centric pattern is to optimise queries, which requires all input
data to be submitted as a single request to back-end services.

The OpenAssetIO API is entirely synchronous. There have been discussions
around the merit of a promise-based variant, but so far all explored
scenarios have favoured a simple blocking API. This is a topic that can
be revisited at a later date should the need arise.

In addition, it is envisaged that a move to a async/concurrent API would
be part of a larger change, and most likely introduced as an alternate
code path, rather than a wholesale change to the existing methods.

Note also that by design, all API methods (aside from initialization)
are thread-safe and may be called concurrently from any number
of threads.

OpenAssetIO as an API is purely middleware. The
`Manager`/`ManagerInterface` pair provides a high-level, interface based
isolation between the implementation of the manager, and host code that
calls API methods.

Due to this fact, a strong steering factor in this decision is to
simplify implementation for a manager. Host-facing conveniences can
be transparently added to the `Manager` wrapper, assuming the underlying
`ManagerInterface` signature chosen is sufficiently flexible.

When considering value exchange across this boundary, it is worth noting
that strategies based on encapsulation require two discreet interfaces
to be maintained. As the API doesn't own either implementation, a
host-facing interface and one for the manager need to be defined. This
generally adds significantly more complexity than when used in a more
traditional single-ended scenario, where the implementation is owned by
the API (as it is with `TraitsData`).

## Options considered

### Option 1

Return an array of 'result or error' objects for each input value.

#### Pros

- More familiar in target languages.
- Facilitates data-centric functional programming without caller-side
  wrapping.
- Data-centric result is easier to propagate across process/host
  boundaries.
- Conceptually simple.
- Supports multiple iteration.

#### Cons

- The result values are complex and requires boilerplate on the host
  side to un-pack.
- Requires additional allocations/copies of the result container.
- Precludes any value-wise processing before the entire batch is ready.

### Option 2

Provide success/error callbacks to be invoked for each input value.

The manager guarantees to invoke one of the callbacks for each input
value on the current thread before the method returns. The order of
calls is not guaranteed.

This allows the method to act as a de-coupling mechanism between the
threading approach of the host and manager. Either one can choose to
internally dispatch work in parallel if desired, without forcing the
other into additional synchronisation mechanisms.

Control flow resides with the manager.

#### Pros

- Flexible, can be wrapped to look like Option 1 or 3 as a
  host-convenience.
- Simplifies value handling on the host-side.
- Facilitates future migration to concurrent (by value) operations via
  parallel callback execution.
- Facilitates future migration to async host-facing APIs (though not as
  cleanly as Option 3).
- Avoids the requirement for all results to be allocated in a single
  container at any one point in time.
- Permits the results for each input value to be processed as they are
  made available, without needing to wait for the entire batch to be
  retrieved. This facilitates parallel operations for slow requests
  and/or subsequent processing operations.
- Potentially simplifies manager implementation as all work can be done
  on the current thread in a synchronous manner with a simple in-line
  implementation.

#### Cons

- Less idiomatic in some target languages, especially Python.
- Precludes data-centric functional programming without caller-side
  wrapping.
- Function-centric result is harder to propagate across process/host
  boundaries.
- Potential for high per-result call cost depending on the language
  stack.
- Interleaved call stack could complicate debugging or runtime-failure
  handling.
- Not as well encapsulated as Option 3.

### Option 3

Return a iterator/result proxy object that yields 'result or error'
objects for each input value.

Value iteration is performed by the host (non-concurrently) in
subsequent program steps.

This effectively moves the synchronisation point of Option 2 from the
`resolve` method to the result proxy object.

Control flow resides with the host.

#### Pros

- Allows an (non-concurrent) asynchronous workflow with no extra effort
  on the host side.
- Result handling could be moved between threads (non-concurrently).
- More idiomatic presentation across target languages.
- Flexible, can be wrapped to look like Option 1 or 2 as a
  host-convenience.
- De-couples the call stack between host/manager (compared to Option 2).
- Facilitates future migration to async (by value) operations.
- Host-controlled iteration potentially avoids the need to retrieve
  un-requested values during partial iteration.

#### Cons

- The result values are complex and requires boilerplate
  on the host side to un-pack  before use.
- Requires additional allocations/copies of the result container.
- Significantly more code to maintain when considering required language
  bindings.
- This solution raises a variety of questions about when work is done:
  - If it is mandated that results are queried during `resolve`, and
    the return is just an opaque view on the data, this is essentially
    a more complex version of Option 1.
  - If it is defined that `resolve` should return _before_ any work is
    done, it could significantly increase the complexity of the
    manager's implementation.
  - If this is left up to the manager's implementation to decide, it
    creates an undefined relative cost of `resolve` vs
    '`results.next()`' that could complicate programming choices for
    the host.
- Adds complexity to the manager's implementation (result proxy classes
  and state management).
- Precludes data-centric functional programming without caller-side
  wrapping.
- Supporting repeat iteration adds complexities or ambiguity as to the
  required behaviour for the manager.
- This solution raises a variety of questions about the order of
  iteration:
  - If it is guaranteed to be in order of the input elements, it
    precludes the ability for the manager to return values 'as they are
    ready'.
  - If out-of-order iteration is allowed, it is perhaps
    counter-intuitive given the conceptual nature of the result
    container as a transformation of the input values. It would also
    require another field in the value holder to provide the input
    index.

## Outcome

OpenAssetIO will use Option 2 - the callback-per-result mechanism for
relevant `ManagerInterface` methods.

## Rationale

We reject Option 1 as it offers the least flexibility, is slower, and
requires a complex value type.

We reject Option 3 as though it may be a more traditional design
pattern, the 'two-headed' nature of OpenAssetIO precludes many of the
benefits this approach traditionally brings without significantly
increased complexity. Additionally, the ambiguity around 'when work is
done', and the question of iteration order further complicates its
execution.

Option 2 has almost comparable flexibility but with significantly less
conceptual and technical overhead. Its runtime behaviour is also simpler
to describe within the presently synchronous/non-concurrent nature of
the API.

We felt Option 2s simplicity was worth the interleaved call stack and
less elegant host-side implementation as these can be addressed through
conveniences in the `Manager` wrapper.

Performance investigations have also demonstrated it to have a lower
overhead in a variety of common use cases compared to the vector-return
approach. These are detailed in Appendix 2.

Note that this choice does not preclude Option 3 being used in a future
async/concurrent form of the API.

## Appendix 1 - Design sketches

Of the three options, we ruled out Option 3 early on based on
manager-facing complexity and increased maintenance overhead.

The following explores the performance characteristics of the remaining
two candidates, using C++ as the target language.

We assume the following data structure used for reporting an error that
is specific to a particular entity reference in the batch

```c++
struct ErrorCodeAndMessage {
  int code;
  std::string message;
};
```

We focus on sketching potential signatures of
`ManagerInterface::resolve`. The signatures of other batch-first
functions follow a similar pattern.

For Option 1, the signature of `resolve()` in C++ thus has the form

```c++
using ResultOrError = std::variant<openassetio::TraitsDataPtr, ErrorCodeAndMessage>;

std::vector<ResultOrError> resolve(const std::vector<EntityRef>& entityRefs,
                                   const std::unordered_set<std::string>& traitSet,
                                   const ContextPtr& context,
                                   const managerAPI::HostSessionPtr& hostSession);
```

For Option 2, the proposed signature uses `std::function` callbacks and
has the form

```c++
using SuccessCallback = std::function<void(std::size_t, TraitsDataPtr)>;
using ErrorCallback = std::function<void(std::size_t, ErrorCodeAndMessage)>;

void resolve(const std::vector<EntityRef>& entityRefs,
             const std::unordered_set<std::string>& traitSet,
             const ContextPtr& context,
             const managerAPI::HostSessionPtr& hostSession
             const SuccessCallback& successCallback,
             const ErrorCallback& errorCallback);
```

where the first `std::size_t` argument to a callback is the relevant
index in the input array of entity references.

## Appendix 2 - Performance

To test the performance of the two approaches, the perftest binary was
updated to evaluate the above sketches in roughly representative
scenarios. The code can be found in the repository under
`resources/perftest/perftest.cpp` (future performance tests may
overwrite this, but the code as used for the following tests will remain
accessible via the git history).

When deciding on the performance impact of one design over another, we
had several concerns

1. Our main concern: is it cheaper to call a callback repeatedly, once
   for each result, or is it cheaper to return an array of results and
   iterate over it?
2. Assuming the user _wants_ an array of results, what is the cost of
   using a callback design anyway, and have the user construct their own
   array?
3. Is there a performance benefit to using raw function pointers rather
   than `std::function`?
4. What is the performance impact of the small-size optimization in
   common `std::function` implementations?

### Test setup

The following results come from a build using with GCC 9.3 on Ubuntu
20.04, compiled in a Release (`O3`) configuration.

Each set of cases is executed over 5000 iterations (epochs), with a
warm-up of 1000 epochs to alleviate CPU scaling artifacts, etc. In
addition, the whole test is executed 5 times (5 runs of the perftest
executable) and the summary results with the lowest standard deviation
taken, on the assumption that this represents the results that are least
skewed by external factors.

A database (simple map of entity reference to URL) of size 10000 is
generated to draw from. Input entity references are randomly chosen from
this database, with the probability of an erroneous entity reference set
to 0.1. Timings are nanosecond precision.

Since we're concerned with the relative performance, the key output of
the perftest is the ratio of timings between two solutions. That is,
dividing the timing of one solution by the timing of another, such that
if the solution in the numerator is faster, the ratio value is greater
than 1, and if the numerator solution is slower, the ratio value is less
than 1. The mean and standard deviation of these timing ratios are
reported in the tables below. We round to 3 significant figures - the
resolution of the fastest results are 3 significant figures (hundreds of
nanoseconds).

As shorthand for the different test cases, we define

- _vector_ as the case that returns an array of results (i.e. Option 1).
- _callback_ as the case that executes a `std::function` callback on
  each result (i.e. Option 2).
- _callbackToVector_ as the case that builds an array as callbacks
  are executed and then iterates over it (i.e. simulating Option 1).
- _callbackFnPtr_ as the case that uses function pointers, rather than
  `std::function`, as the callback.
- _callbackLargeCapture_ as the case that uses a `std::function`
  callback holding a lambda with capture data such that the small-size
  optimisation is unavailable.

### Batch size = 1

The following tables gives the results of the (likely) usual case of a
batch size of 1 (i.e. only querying a single entity reference).

Firstly, the primary results comparing the array return value solution
versus the `std::function` callback solution is shown below.

| numerator/denominator     | mean | std dev |
|---------------------------|------|---------|
| vector/callback           | 1.29 | 0.761   |
| vector/callbackToVector   | 1.15 | 0.570   |

The secondary test results investigating the performance impact of
function pointers and large lambda captures are presented in the
following table.

| numerator/denominator         | mean | std dev |
|-------------------------------|------|---------|
| callbackFnPtr/callback        | 1.09 | 0.600   |
| callbackLargeCapture/callback | 1.40 | 0.758   |

### Batch size = 100

The following tables give the results using a larger batch size of 100.

Firstly, as before, the primary results are shown below.

| numerator/denominator     | mean | std dev |
|---------------------------|------|---------|
| vector/callback           | 1.44 | 0.230   |
| vector/callbackToVector   | 1.08 | 0.192   |

And again, the secondary test results are shown below.

| numerator/denominator         | mean | std dev |
|-------------------------------|------|---------|
| callbackFnPtr/callback        | 1.00 | 0.121   |
| callbackLargeCapture/callback | 1.01 | 0.148   |

### Conclusion

Overall, it seems clear that a callback design is the most performant.

With a small batch size, the standard deviation in timing ratios is so
large that in practice there is little discernible difference in the
options. However, it does appear that the callback solution has the edge
slightly.

Interestingly, using callbacks and appending to a vector on the caller
side (_callbackToVector_) appears slightly more performant than simply
returning a vector directly (_vector_). This could be due to compiler
intricacies (e.g. moving the vector across the DSO boundary), but more
investigation is required.

However, with larger batches we start to see the performance
characteristics of the chosen option dominate over external factors.
Here, the callback solution(s) is the clear winner.

With regard to the secondary tests, we can conclude that there is little
to no significant difference between a `std::function` (_callback_) and
a function pointer (_callbackFnPtr_) for our use-case.

Triggering a dynamic allocation in `std::function` by passing a lambda
with a large capture (_callbackLargeCapture_) appears to have a much
lower impact for large batch sizes than smaller batch sizes. Presumably
this is because the dynamic allocation is only performed once per batch.
So execution of the callback, rather than allocation, dominates with
large batches. However, more investigation is required to be certain.
