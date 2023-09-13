# DR020 Coding style

- **Status:** Decided
- **Driver:** @foundrytom
- **Approver:** @felltech @carmenpinto @fnRaihanKibria
- **Outcome:** OpenAssetIO will use the Google C++ Style Guide.

## Background

OpenAssetIO is a collaboratively maintained codebase. A consistent
coding style can help simplify maintenance. As such, contributors need
clear guidelines.

## Options considered

### Option 1 - Define a custom style guide

Maintainers define a bespoke style guide that embodies their
locally agreed preferences.

#### Pros

- Allows local consensus around what is (personally) preferable in the
  code base.
- Allows a style to be designed that best fits the project, e.g. to
  balance idiomatic differences in a multi-language project.
- Encourages constant adaptation and optimization as the project and
  tooling changes over time.

#### Cons

- Consensus is nigh on impossible when it comes to subjective choices
  such as code style, as the number of contributors grows beyond one.
  Often resulting in unbalanced compromise.
- Disagreements over the style may well be directly attributable to a
  specific individual within the community, that then becomes the target
  of criticism.
- Local control over style minutiae adds the temptation to futz with it
  over time, ultimately reducing overall consistency.
- May increase the complexity of linter configuration when attempting
  to encode the agreed standard.

### Option 2 - Use a common well-established standard

Pick a well known existing standard and just use that.

#### Pros

- Significantly reduces the complexity of the decision space as it is
  now simply picking one of several presets instead of every aspect of a
  style guide.
- The details of the style are not owned by the project, deflecting
  disagreements to an abstract third party, and removing the temptation
  to futz.
- Likely that most contributors will have some (individual)
  disgruntlement with the style, sharing the feeling of compromise.
- If a popular standard is chosen, it may be supported out-the-box by
  linters.
- Can always be tweaked to better suit the team (e.g. line length
  limits) or to cover additional areas that the standard has no opinion
  on.

#### Cons

- Likely that most contributors will have some (individual)
  disgruntlement with the style.
- Risk that some sensible exceptions to the style guide, which could
  improve team effectiveness, may not be considered.
- Existing style guides are invariably language-specific. Languages in a
  multi-language project risk being either conformed to a non-idiomatic
  style, or made inconsistent with other languages.
- A pre-existing style guide (and tooling enforcing it) does not
  necessarily cover everything. This can lead to a false sense of
  security, in turn leading to growing inconsistencies that are not
  addressed.

## Outcome

OpenAssetIO will pick an off-the-shelf standard, to avoid the
rabbit-hole, and protect contributors from disagreements over minutiae
of the style itself.

Through a majority vote, the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
was selected as being the "least offensive to the largest number of
people".
