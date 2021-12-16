# DR002 Getter method naming

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @foundrytom
- **Approver:** @feltech @foundrytom @TomFoundry
- **Contributors:** @feltech @foundrytom @TomFoundry
- **Outcome:** Remove `get` prefix when not partnered with a `set`

## Background

We aim to create a codebase that is as easy to mentally parse as
possible. Naming schemes for symbols are crucial in aiding readability.

A common pattern for accessor (getter) methods/functions is to begin the
function name with `get`, and historically OpenAssetIO liberally used
this convention for such functions. However, there are alternative
schemes that might help developers viewing a cross-section of the
codebase to make better inferences about the wider codebase.

## Relevant data

This decision was made with reference
to [one of the early RFCs](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/5)
for OpenAssetIO.

Alternative coding conventions include

* Oracle [Java-style](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html):
  > Methods should be verbs ... [e.g.] getBackground

* Google [C++-style](https://google.github.io/styleguide/cppguide.html#Function_Names):
  > Accessors and mutators (get and set functions) may be named like
  > variables. ... For example, int count() and 
  > void set_count(int count).

  and [Python style](https://google.github.io/styleguide/pyguide.html#315-getters-and-setters):
  > Getters and setters should follow the Naming guidelines, such as
  > get_foo() and set_foo().

## Options considered

### Option 1

Prefix all getters with `get`.

#### Pros

- No change in the current codebase.
- Removes any potential ambiguity - a `get` method is always an
  accessor.

#### Cons

- The `get` is often redundant.
- If side effects are introduced then the method name must change to
  avoid misleading developers.

Estimated cost: None

### Option 2

Only prefix getters with `get` if there is a corresponding `set`.

#### Pros

- Readers can tell at a glance if a `get` accessor has a corresponding
  `set` mutator.
- Concise method/function names.

#### Cons

- Requires extensive API changes.

Estimated cost: Small

## Outcome

We choose to remove the prefix from getters where there is no
corresponding setter. We believe the work to refactor the codebase is
justified given the benefit to readability this gives.
