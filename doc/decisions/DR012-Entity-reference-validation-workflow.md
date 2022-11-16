# DR012 Entity reference validation workflow

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @feltech
- **Approver:** @foundrytom
- **Outcome:** Support all options: `isEntityReferenceString`, and both
  throwing and `optional`-based variants of `createEntityReference`

## Background

The current API's `Manager.isEntityReferenceString` must be called by
a host before the entity reference is used. This is a brittle mechanism
based on trust.

The result of [DR011](DR011-Entity-reference-type-safety.md) was to use
strongly typed identifiers for entity references instead. This allows
(some) compile-time guarantees, extensibility, and opens up additional
validation options.

However, `isEntityReferenceString` is also useful for the host, allowing
it to (cheaply) decide whether to use an assetized or non-assetized code
path when given a string to process.

This begs the question, with the new strong typing mechanism, what is
the host workflow for deciding on asssetized vs. non-assetized code
paths?

## Relevant data

A host may find themselves with one or more strings that must be
checked to see whether they are an entity reference, before taking the
appropriate code path.

For example, a FileWrite widget may store a raw file path, or may store
an entity reference. In the former case the code path would perform a
non-assetized workflow, in the latter case the code path would typically
need to validate the entity reference, call `preflight`, write the file,
then call `register`.

Another example could be a node graph that is optimised to prefetch
nodes' associated scripts in a batch. In this case, each node may store
a raw file path, or may store an entity reference. The host must iterate
over the nodes and decide which should use a direct file load
and which need to be `resolve`d first, then take the appropriate code
path.

We can assume that testing whether a string is an entity reference,
relevant to a given manager, is a cheap operation. It is performed
entirely in-process within the plugin (possibly even in the middleware
if a prefix is given by `Manager.info()`). In an analogy to URLs,
`isEntityReferenceString` is like checking the URL schema. In
particular, this means entity-specific details, e.g. whether a URL query
parameter is relevant for the type of entity being referenced, is out of
scope for `isEntityReferenceString`.

The sketch of the `Manager.createEntityReference` method from
[DR011](DR011-Entity-reference-type-safety.md) assumes the method throws
if given an invalid reference, which means the only way an `EntityRef`
type is constructed is when a manager (not necessarily the appropriate
manager) has deemed an entity reference to be valid. In this way we
have a partial C++ compile-time guarantee to methods that take entity
reference arguments, such as `resolve`, that the `EntityRef`s provided
have been validated.

### References

See issue [#532](https://github.com/OpenAssetIO/OpenAssetIO/issues/532).

## Options considered

### Option 1

Allow hosts to call `isEntityReferenceString` as well as
`createEntityReference` (which throws if given an invalid reference).

#### Pros

- No need to (try to) construct an object just for a boolean comparison.
- Obvious self-documenting usage.
- Clear language bindings based on existing patterns.
- No way to construct an invalid entity reference.

#### Cons

- Duplicated validation effort if the code path goes on to use
  `createEntityReference`.
- Hosts may forget to check `isEntityReferenceString` first, leading to
  unexpected exceptions.

### Option 2

`isEntityReferenceString` is hidden from the host.
`createEntityReference` is the only way to construct and validate an
entity reference, and throws if invalid.

#### Pros

- Only one way to accomplish validation and construction.
- Validation and construction are performed in one operation.
- Clear language bindings based on existing patterns.
- No way to construct an invalid entity reference.

#### Cons

- Host must use exceptions to test validity, increasing boilerplate
  and reducing performance.
- If the host just wants to test validity (e.g. in order to choose a
  code path), then there is no way to do this without also constructing
  a throwaway object.

### Option 3

`isEntityReferenceString` hidden from the host.
`createEntityReferenceIfValid` is instead used to return an
`optional<EntityRef>` in C++ (`None`/`EntityRef` in Python; `NULL` (and
error code)/`EntityRef_h` in C).

#### Pros

- Only one way to accomplish validation and construction.
- Validation and construction are performed in one operation.
- Lowest host boilerplate for many workflows, utilising modern C++.
- If using  `optional::value()` to extract the `EntityRef` before
  passing to API methods, then safety is guaranteed, since a
  `bad_optional_access` will be thrown if invalid (though less
  informative than a custom exception).
- Pybind has built-in support for `std::optional`, translating "not set"
  to `None`.

#### Cons

- Very slightly less performant than `isEntityReferenceString` in the
  invalid reference case (at the risk of second-guessing compiler
  optimisations).
- Not immediately obvious in Python that the host must test the returned
  value is valid (not `None`).
- Uses a different optional API to `TraitsData`, decided
  in [DR010](DR010-TraitsData-value-retrieval-API.md).
  Though many of the arguments do not hold for this case (e.g.
  direct-assignment to existing variables; detailed result codes).
- Using the dereferencing operator (`*`) on a `std::optional` is unsafe
  and loses the compile-time guarantee that the entity reference is
  safe before being passed to API methods.
- Language bindings to C and Python have a different interface than C++.

## Outcome

Based on the sketches in the Appendix (below) and the various pros and
cons we have decided on supporting all workflows, i.e. implementing
Option 1 and 3 (with Option 2 supported implicitly).

The number of potential host workflows, which we have little visibility
on at present, mean that all options have enough merits to warrant
first-class inclusion in the core API.

## Appendix

### Sketch - Publishing from a FileWidget

We assume a `FileWidget` that may either contain a path or an entity
reference, and the application must take a different code path for
each case.

#### Option 1

```python
file_path_or_ref = file_widget.get_value()

if manager.isEntityReferenceString(file_path_or_ref):
    # Note: duplicated validation.
    ref = manager.createEntityReference(file_path_or_ref)
    assetized_publish(ref)
else:
    publish(file_path_or_ref)
```

#### Option 2

```python
file_path_or_ref = file_widget.get_value()

try:
    ref = manager.createEntityReference(file_path_or_ref)
except InvalidEntityReferenceError:
    publish(file_path_or_ref)
else:
    assetized_publish(ref)
```

#### Option 3

```python
file_path_or_ref = file_widget.get_value()

if ref := manager.createEntityReferenceIfValid(file_path_or_ref):
    assetized_publish(ref)
else:
    publish(file_path_or_ref)
```

### Sketch - Assetized workflow is unsupported

We assume an application with a code path that does not support
an assetized workflow, and so rejects strings that are entity
references.

#### Option 1

```python
file_path_or_ref = file_widget.get_value()

if manager.isEntityReferenceString(file_path_or_ref):
    raise TypeError("Assetized workflow is not yet supported")

process_file_path(file_path_or_ref)
```

#### Option 2

```python
file_path_or_ref = file_widget.get_value()

try:
    manager.createEntityReference(file_path_or_ref)
except InvalidEntityReferenceError:
    pass
else:
    raise TypeError("Assetized workflow is not yet supported")

process_file_path(file_path_or_ref)
```

#### Option 3

```python
file_path_or_ref = file_widget.get_value()

if manager.createEntityReferenceIfValid(file_path_or_ref):
    raise TypeError("Assetized workflow is not yet supported")

process_file_path(file_path_or_ref)
```

### Sketch - Resolving a batch of references

We assume a node graph where each node is associated with a script file
to be loaded. The script file loading process is executed for all nodes
batched together. A node may have a raw file path or may have an
entity reference pointing to the script. We are unsure during the
loading process whether a node stores a raw file path or an entity
reference.

#### Option 1

```python
refs = []
paths = []
assetized_nodes = []
nonassetized_nodes = []

for node in node_graph:
    file_path_or_ref = node.get_script()

    if manager.isEntityReferenceString(file_path_or_ref):
        assetized_nodes.append(node)
        ref = manager.createEntityReference(file_path_or_ref)
        refs.append(ref)
    else:
        nonassetized_nodes.append(node)
        paths.append(file_path_or_ref)

# Process nodes whose script path is a raw file system path.

for node, path in zip(nonassetized_nodes, paths):
    node.load_from_file(path)


# Process nodes whose script path is an assetized url.

def success_callback(idx, traits_data):
    node = assetized_nodes[idx]
    url = LocateableContentTrait(traits_data).getLocation()
    node.load_from_url(url)


def error_callback(idx, error):
    log.error(error.message)


manager.resolve(refs, {LocateableContentTrait.kID}, context,
                success_callback, error_callback)
```

#### Option 2

```python
refs = []
paths = []
assetized_nodes = []
nonassetized_nodes = []

for node in node_graph:
    file_path_or_ref = node.get_script()

    try:
        ref = manager.createEntityReference(file_path_or_ref)
    except InvalidEntityReferenceError:
        nonassetized_nodes.append(node)
        paths.append(file_path_or_ref)
    else:
        assetized_nodes.append(node)
        refs.append(ref)

# ... Remainder is identical to option 1 ...
```

#### Option 3

```python
refs = []
paths = []
assetized_nodes = []
nonassetized_nodes = []

for node in node_graph:
    file_path_or_ref = node.get_script()

    if ref := manager.createEntityReferenceIfValid(file_path_or_ref):
        assetized_nodes.append(node)
        refs.append(ref)
    else:
        nonassetized_nodes.append(node)
        paths.append(file_path_or_ref)

# ... Remainder is identical to option 1 ...
```

### Sketch - Processing references from an AssetWidget

We assume a widget that has prior knowledge that the strings it stores
are pre-validated asset references (perhaps coming from UI delegation to
a manager plugin) against a known manager.

We further assume that switching to a different manager plugin and
attempting to use a now-incorrect entity reference from the
`AssetWidget` is a rare exceptional case.

#### Option 1 / 2

We're already certain that the paths are valid for the current manager,
and so do not need to check `isEntityReferenceString`.

```c++
auto ref_str = asset_widget->getValue();
// We assume the ref is relevant to the selected manager, i.e. it's
// exceptional if not, and expected that this call will throw in that
// case.
auto ref = manager.createEntityReference(ref_str);
process_entity_reference(ref);
```

#### Option 3

Although we're certain that the paths are valid, we must nevertheless
unpack an `optional`.

```c++
auto ref_str = asset_widget->getValue();
std::optional<EntityRef> ref = manager.createEntityReferenceIfValid(ref_str);
// Unsafe! We must _really_ be sure.
process_entity_reference(*ref);
// Alternatively, much safer - throws `bad_optional_access` if ref is invalid.
process_entity_reference(ref.value());
```
