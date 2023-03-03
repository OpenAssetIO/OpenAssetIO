# DR015 Strategy for methods with several signature variations

- **Status:** Decided
- **Impact:** Low
- **Driver:** @foundrytom
- **Approver:** @feltech @elliotcmorris @mattdaw
- **Outcome:** OpenAssetIO will use overloads where possible, and simple
  signature-describing suffixes if not.

## Background

Methods within the OpenAssetIO API may serve the same logical purpose,
but have different signatures or return types. An example of this being
callback or return value variations of the `resolve` call.

Some programming languages allow methods to be declared with the same
name and different signatures (e.g. Function Overloading in C++). This
is by no means universal though.

We need to determine a strategy for the declaration of such methods
within the API that provides the best developer experience and coherence
with the rest of the project.

> **Note:**
> This DR is concerned with how to name/present the methods, rather than
> the specifics of any particular signature/calling convention.

## Relevant data

- OpenAssetIO supports multiple languages (currently C, C++, Python),
  each with their own syntax and language rules. It will certainly be
  extended in the future to as yet unknown languages with similarly
  unknown constraints.

- OpenAssetIO strives for coherence between languages as many developers
  have to work in multi-language code bases. There are certainly
  concessions if this leads to idiosyncrasies, but ideally terminology
  and semantic structure is coherent wherever possible.

The examples illustrated in the options below focus on the case of
providing "host conveniences" for the batch-centric API methods. The
OpenAssetIO batch API uses the following canonical from:

```c++
void someSingularName(inputVector, ..., successCallback, errorCallback);
```

The rationale for this form is covered
[here](./DR009-Batch-method-result-types.md) and
[here](./DR003-ManagerInterface-method-naming.md). The salient points of
the purposes of this discussion are:

- There is no return value.
- The `successCallback` is called for each element of the input vector
  that is processed without error.
- The `errorCallback` is called for any element of the input vector that
  resulted in a processing error.

Though this is flexible, and supports future design patterns, it can add
significantly to the host implementation boilerplate for simple tasks
such as resolving a single reference where any error is considered
exceptional.

We desire to add several host-facing conveniences that simplify common
API interactions. This immediately precipitates the discussion as to how
these should be integrated into the API.

We have previously ruled out the use of wrappers or more advanced
chainable structures due to complexity, broader language support, and as
they preclude the ability for the manager plugin to provide optimized
implementations in the future.


## Options considered

### Option 1

Use function overloading where possible.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback);
void resolve(vector<T> inputs, vector<variant<ValueType, Error>> &out);
void resolve(vector<T> inputs, vector<ValueType> &out);
void resolve(T input, variant<ValueType, Error> &out);
void resolve(T input, ValueType &out);

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback);
void entityVersions(vector<T> inputs, vector<variant<ValueType, Error>> &out);
void entityVersions(vector<T> inputs, vector<ValueType> &out);
void entityVersions(T input, variant<ValueType, Error> &out);
void entityVersions(T input, ValueType &out);
```

#### Pros

- Low cognitive overhead to determine which high-level API method is
  being invoked as the name contains no other information.
- Avoids awkward compromises in determining method name mutations.

#### Cons

- Not supported in many languages.
- High cognitive overhead in understanding which variation is being used
  as it relies on parameter naming and/or type visibility.
- Forces out-params in C++ as overloading can't be based on return type.
- Hides implicit conversions.

### Option 2

Describe the variation as a continuation of the method name.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback);
vector<variant<ValueType, Error>> resolveToErrorOrResultVector(vector<T> inputs);
vector<ValueType> resolveToResultVector(vector<T> inputs);
variant<ValueType, Error> resolveOneToErrorOrResult(T input);
ValueType resolveOneToResult(T input);

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback);
vector<variant<ValueType, Error>> entityVersionsAsErrorOrResultVector(vector<T> inputs);
vector<ValueType> entityVersionsAsResultVectory(vector<T> inputs);
variant<ValueType, Error> entityVersionsForOneToErrorOrResult(T input);
ValueType entityVersionsForOneToResult(T input);
```

#### Pros

- Low cognitive overhead in understanding which variation is in use as
  it is clearly described.

#### Cons

- Higher cognitive overhead to determine which high-level API method is
  being invoked, as the boundary between method name and variation is
  variable. Though this could be mitigated with a separator, e.g.
  `resolve_ToErrorOrResultsVector`.
- The variation description is not consistent as grammar requires some
  variation based on the method name.
- The above two points could add higher cognitive overhead for
  non-native speakers.
- Longer method names could cause line length considerations.

### Option 3

Suffix method names to describe variations

- `S` Singular input/output (non-batch).
- `R` Return data.
- `E` Raise an exception on first error.

```c++
void resolve(vector<T> inputs, F* successCallback, F* errorCallback);
vector<variant<ValueType, Error>> resolve_R(vector<T> inputs);
vector<ValueType> resolve_RE(vector<T> inputs);
variant<ValueType, Error> resolve_SR(T input);
ValueType resolve_SRE(T input);

void entityVersions(vector<T> inputs, F* successCallback, F* errorCallback);
vector<variant<ValueType, Error>> entityVersions_R(vector<T> inputs);
vector<ValueType> entityVersions_RE(vector<T> inputs);
variant<ValueType, Error> entityVersions_SR(T input);
ValueType entityVersions_SRE(T input);
```

This version could also introduce a `B` batch prefix, to be added to
existing methods.

> **Note:**
> The use of uppercase letters for the suffix over lowercase is to avoid
> ambiguity when multiple letters are present, as they are more likely
> to be read as a word, and will be properly split by a de-camel-case
> operation.

#### Pros

- Lower cognitive overhead to determine which high-level API method is
  being invoked, as the variation is separated from the method name.
- Shorter method names help with overall line length considerations.
- Conveys the impression that these are merely conveniences more clearly
  as the "wordy" part of the name is constant with the baseline form.

#### Cons

- Higher cognitive overhead to determine which variation is in use as
  it follows an opaque convention.
- The number of suffixes could become hard to remember.
- Suffixes could collide, across different parts of the API.

## Outcome

OpenAssetIO will adopt a hybrid of the above options:

- Function overloads and other language-idiomatic features should be
  used when available.
- Signature suffixes should be used where there names are the only way
  to differentiate.

The format of the suffixes is as follows:

```
<methodName>_<inputType><outputMethod><outputValueType>
```

Where:

- `<inputType>` is one of `S` (single) or `B` (batch).
- `<outputMethod>` is one of `C` (callback) or `V` (value).
- `<outputValueType>` is one of `R` (result variant) or `D` (data).

Examples of this approach applied to our currently supported languages
are shown below.

> **Note:**
> The actual signatures are illustrative and aren't intended to be the
> final incarnations.

### C++

C++ can use function overloading and other language features to avoid
the need for naming variation:

```c++
void resolve(vector<T> inputs, ..., F* successCallback, F* errorCallback);
vector<variant<ValueType,Error>> resolve<OutputValueType::kResult>(vector<T> inputs, ...);
vector<ValueType> resolve<OutputValueType::kData>(vector<T> inputs, ...);

void resolve(T input, ..., F* successCallback, F* errorCallback);
variant<ValueType,Error> resolve<OutputValueType::kResult>(T input, ...);
ValueType resolve<OutputValueType::kData>(T input, ...);
```

(Could always use out-params instead of template driven return
types if preferred.)

### Python

Pythons late-bound nature and pybind's support for overloads means that
we can simulate function overloading whilst also taking advantage of
native support for mixed types in a list.

```python
resolve(inputOrInputs: T|list[T], successCallback, errorCallback) -> None
resolve(inputOrInputs: T|list[T], raiseOnBatchElementError=True) -> varies
```

### C

Standard C's limited feature set requires us to make use of the naming
suffixes, and alternate approaches to result propagation.

```c
int resolve_BCD(TVectorHandle inputs, F* successCallback, F* errorCallback, ...);
int resolve_BVR(TVectorHandle inputs, ResultVectorHandle out, ...);
int resolve_BVD(TVectorHandle inputs, ValueTypeVectorHandle out, ...);

int resolve_SCD(THandle input, F* successCallback, F* errorCallback, ...);
int resolve_SVR(THandle input, ResultHandle out, ...);
int resolve_SVD(THandle input, ValueTypeHandle out, ...);
```

### Rationale

There was no strong consensus in the community in terms of the two
specific naming conventions. Concern was also raised as to the loss of
language-specific features explicitly designed to help avoid this
problem in the first place. Our hybrid approach seemed to offer the
biggest win:

- Naming is as consistent as it can be, when squinting, as we avoid
  renaming just because of convention.
- The API has a richer and more 'native' feel in each language as its
  full feature set can be employed.

The use of the single letter suffix vs the wordier alternative
was driven by the potential to use the convention to automate
binding generation for other languages. As C is a common base for FFIs,
and C is the one most in need of name-based disambiguation, this felt
like enough of a weighting factor, over the otherwise more
cosmetic/personal reasons for selection. At present, the majority of
end-developer target languages don't require suffixes, and so we hope
the opaque nature of the suffix is not a practical problem for code-base
readability in general use.
