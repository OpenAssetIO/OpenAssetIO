# DR006 C++ generic string type

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @feltech
- **Approver:** @foundrytom
- **Contributors:** @feltech @foundrytom @meshula @carmenpinto
- **Outcome:** Use `std::string`/`std::string_view` with appropriate
  typedefs.

## Background

Originating [GitHub issue](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/193).

We must decide what generic string type should be exposed in the C++
API.

Strings are a core data type of OpenAssetIO, used as both input and
output of entity references and URIs, as well as nested within
dictionary types for entity attributes and specifications.

Language bindings must also be considered. Python is a special-case
due to the tight coupling with the C++ implementation (via
pybind11). Other language bindings will build upon a C API, so some
care must be taken to ensure binding our string type to C is feasible.

### Assumptions

* Some strings should be strongly typed, e.g. entity references, but we
  still require a generic string type for some purposes.
* UTF-8 encoding is used throughout, wherever there is a choice. Any
  necessary conversions (e.g. for Windows UIs/files) is the
  responsibility of the host/plugin.
* Python is restricted to Python 3, where we use the native `str`
  type, which is unicode but [not necessarily](https://docs.python.org/3/c-api/unicode.html)
  UTF-8. However, we assume C++ bindings via [pybind11](https://pybind11.readthedocs.io/en/stable/advanced/cast/strings.html),
  which encodes Python->C++ strings as UTF-8 (`char*` or
  `std::string`) and expects pre-encoded UTF-8 strings for
  C++->Python.
* We must consider C bindings, but that implementation detail is left
  for future work.

## Relevant data

### Library survey

[vfx-rs](https://github.com/vfx-rs) is a project to create Rust
bindings by way of C bindings for various popular VFX open source
projects.

The vfx-rs project reveals that USD and OpenEXR use `std::string`.

USD additionally has its own `SdfPath` type that can be converted
to/from `std::string` and `char*`.

OpenImageIO on the other hand (primarily) uses a custom `ustring`
type. This uses a global hash table of all strings in order to provide
fast comparisons. They also use `std::string` and a custom `string_view`
class.

All the above vfx-rs bindings projects expose string classes as opaque
handles in C with a C REST-like API for operating on them. Other
vfx-rs projects seem incomplete at the moment.

Looking at other [ASWF-maintained projects](https://github.com/orgs/AcademySoftwareFoundation/repositories?type=all):
OpenVDB uses `std::string`; OpenShadingLanguage relies on
OpenImageIO string types plus a custom CUDA-compatible string type;
Imath uses `std::string` extensively in its Python bindings, but has
little use for strings in C++.

### References

* [GCC C++11 ABI break](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_dual_abi.html)
  ([VFX reference platform](https://vfxplatform.com/) is currently stuck
  on the old ABI).
* [ACCU Overload, 21(116):11-15, 2013](https://accu.org/journals/overload/21/116/steinbach_1842/)
  article on portable string literals.
* [utf8everywhere](http://utf8everywhere.org/) article promoting "just
  use UTF-8".
* Google Abseil library's [string types/functions](https://abseil.io/docs/cpp/guides/strings)
  has some notes on `string_view` constants and lifetime.
* vfx-rs's [cppmm](https://github.com/vfx-rs/cppmm) semi-automated
  C++->C bindings generator.
* [UTF8-CPP](https://github.com/nemtrif/utfcpp) C++ library provides
  functions for operating on UTF-8 strings stored within a
  `std::string`.
* IBM's [ICU](https://icu.unicode.org/) popular heavyweight C
  (unicode) string library with custom types.
* [CsString](https://github.com/copperspice/cs_string) C++ library
  providing dedicated unicode-aware string types.
* [LabText](https://github.com/meshula/LabText) C-native string
  library with C++ wrappers.
* [SDS](https://github.com/antirez/sds) Redis's C-native string
  library.


## Options considered

### Option 1

`std::string_view` for string literal constants; `std::string` or
`std::string_view` (as appropriate) for parameters/values.

#### Pros

- Little boilerplate required to integrate into existing C++ code
  bases.
- Straightforward manipulation by `std::string`-compatible library
  functions.
- Consistent with other VFX open source projects (see above).

#### Cons

- Ties us to a specific underlying class that cannot be extended.
- Sensitive to ABI differences between compilers (e.g. GCC C++11 ABI
  break, see above).
- Sensitive to cross-platform implementation differences.
- The correct interpretation of a string's bytes is left as an exercise
  to the reader, no details of encoding, etc. is associated with the
  value.

Estimated cost: Small

### Option 2

Custom type with hidden implementation ([pimpl](https://en.cppreference.com/w/cpp/language/pimpl)).

#### Pros

- Compiler/library isolation.
- Allows use of intrusive smart pointers (e.g.
  `enable_shared_from_this`).
- Can be extended with custom logic for validation, encoding, etc.
- Implementation can be extended without breaking ABI compatibility of
  hosts/plugins.
- A third-party library can be used under-the-hood.

#### Cons

- Additional boilerplate required, e.g. converting to/from native types,
  and custom Python pybind11 converters.
- (Small) performance hit of additional pointer indirection to
  implementation.

Estimated cost: Medium

### Option 3

Exposing a third-party library.

#### Pros

- No reinventing the wheel for (common) string functions.
- Assuming a well-behaved cross-platform library, the behavior is
  potentially more predictable than the standard library across
  different toolchains.
- A C-native library (with C++ wrappers) would avoid the need for
  roll our own C bindings.

#### Cons

- Additional third-party dependency - especially problematic if exposed
  as a core type required by adopters, and even worse if adopters are
  already using a different (or customized) version of the library.
- Custom Python converters required.

Estimated cost: Medium

## Outcome

We decided on Option 1.

This option seems to reflect the prevailing string treatment in the
community. It offers the path of least resistance for bindings, both
to Python and C.

Our assumption of UTF-8 throughout, and our lack of a need for complex
string parsing and manipulation, mean that we don't expect to require
functionality much beyond what `std::string` offers. Any additional
functionality (e.g. tokenizing UTF-8 strings) can be handled as a
(hidden) implementation detail, potentially using one of the
several existing third-party libraries that operate on `std::string`.

We will take advantage of the current "alpha" state of the project to
further explore and battle-test the practical ramifications of this
choice. We will have time before an initial release to change the
implementation should significant issues arise.

Even beyond that point, one way we can partially mitigate the cost of a
redesign is by appropriate use of `typedef`s (including referring
exclusively to those typedefs in the C opaque pointer API).

Potential ABI and cross-platform issues are a concern, but until we
gather more evidence these potential problems are insufficient to
justify the complexity of the alternatives.
