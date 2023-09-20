# DR021 Cross-language consistency

- **Status:** Decided
- **Driver:** @foundrytom
- **Approver:** @feltech
- **Outcome:** OpenAssetIO prioritizes consistency across languages over
  local idioms.

## Background

OpenAssetIO, as a C++ project, adopted the well-established Google C++
Style Guide (see [DR020](./DR020-Coding-style.md)), but the project is
bound to multiple other languages.

Elements of the style guide are at odds with equivalent guides in other
languages (e.g. Python's [PEP-8](https://peps.python.org/pep-0008)), and
idiomatic C++ is similarly different at the syntax level to other
targets.

The project may be bound to additional, as yet unknown languages in the
future.

We need a guiding principle that dictates how language bindings should
approach situations where convention differs.

## Relevant data

- Users may well be integrating the project into multiple languages
  simultaneously. For example, many DCC tools are written in a
  combination of C++ and Python. Manager authors may split their plugin
  implementation between the same two languages based on performance
  and/or maintenance overhead.

- The project has limited resource to provide examples and other
  training material.

- Other projects in the ecosystem have opted for consistency between
  languages over local idioms (e.g. [OpenUSD](https://openusd.org),
  [Gaffer](https://github.com/gafferHQ/gaffer)).

## Options considered

### Option 1 - Conform to local idioms in each language

The API surface area will be adapted as much as possible to conform to
the local idioms of each language.

For example, getters/setters in C++ would be converted to properties in
Python.

#### Pros

- The programming experience is intuitive in each language.
- Language-specific features can be used to simplify/optimize code.

#### Cons

- Documentation and examples need to be re-written for each language
  individually.
- Higher cognitive load for developers frequently switching between
  languages in the same project.

### Option 2 - Attempt to align syntax where possible

The API surface area will attempt to remain as consistent as possible
across languages.

For example, getters/setters would exist as class methods in both C++
and Python.

#### Pros

- Documentation and examples are more readily re-used across languages.
- Lower cognitive load for developers frequently switching between
  languages in the same project.

#### Cons

- The programming experience is less intuitive in each language.
- Lose the ability to leverage language-specific features to
  simplify/optimize code.

## Outcome

OpenAssetIO will aim for consistency across languages over local idioms
where possible, and where it doesn't significantly detriment usability.

As such, we accept that aspects of the API may seem 'unusual' in some
cases.

Exceptions may be made where there are minor syntactic differences, but
the concepts are closely aligned, or where certain
features are simply unavailable. See the appendix for more details.

### Rationale

The primary driving factors are:

- Familiarity in multi-language integrations, which are very common.
- Lack of resource to maintain per-language documentation and examples.
- Prior art in closely related projects in the industry.

## Appendix - Notable exceptions

There are certain situations where functionality is simply not
available, or usability would be significantly affected if literal
equivalence was employed. In these cases, or where the differences are
inconsequential, it is appropriate to adapt to the target language
conventions.

- In python returning `None` vs binding `std::optional`.
- In python returning varying types vs binding `std::variant`.
- Adding conveniences such as Python's `__str__` method or C++ `<<`
  operator support.
- Language specific style guides around white-space, literals et al.
  that don't affect identifiers.
- Using opaque handles with mutator methods in C vs classes in C++ and
  Python.
