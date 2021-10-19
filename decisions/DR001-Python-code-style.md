 # DR001 Python code style

- **Status:** Decided
- **Impact:** Medium
- **Driver:** @feltech
- **Approver:** @feltech @foundrytom @fn-yves @TomFoundry
- **Contributors:** @feltech @foundrytom @fn-yves @TomFoundry
- **Outcome:** Use PEP8 with partial exemption for line-wrapping and 
  using C++ naming scheme.

## Background

We are embarking on a mixed-language (Python/C++) open-source project
and wish to ensure a consistent and sensible code style. For Python
there is a de-facto standard coding style specified by the [PEP8](https://www.python.org/dev/peps/pep-0008)
convention, which has good tooling support. 

However, PEP8 does not account for mixed-language projects and may 
otherwise dictate standards that we wish to diverge from to ease 
development.

## Relevant data

The official [PEP8 docs](https://www.python.org/dev/peps/pep-0008) are
used for reference.

A [pull request](https://github.com/TheFoundryVisionmongers/OpenAssetIO/pull/49)
has been created to apply formatting to the codebase, which was reviewed
and updated based on feedback. In particular, line-wrapping was revised.

## Options considered

### Strict PEP8 

Strictly adhere to all PEP8 guidelines.

#### Pros

 - Avoids any interpretation or argument.
 - Familiarity for potential contributors.

#### Cons

 - Divergence from our C++ coding conventions (e.g. camelCase naming).
 - Requires renaming every symbol in the current codebase.
 - 79 character max line length resulted in wrappings with poor
   readability with the current codebase.

Estimated cost: Medium

### PEP8 with exceptions

Stick to PEP8 for Python, but 
* Use our C++ camelCase convention for the naming scheme
* Extend the line length for code to 99 characters

The second point is [explicitly mentioned](https://www.python.org/dev/peps/pep-0008/#maximum-line-length) 
in the PEP8 docs
> it is okay to increase the line length limit up to 99 characters, 
> provided that comments and docstrings are still wrapped at 72 
> characters.

#### Pros

 - Closer parity with our C++ naming scheme, allowing for easier.
   mental parsing of Python/C++ functional equivalences.
 - Fewer changes to existing codebase.
 - A 99 char line length means code spans fewer lines, making it easier 
   to comprehend, whilst still providing sufficient space for 
   side-by-side dev/diff on modern screens.

#### Cons

 - Naming scheme is more open to interpretation and could cause code 
   review churn.
 - Configuration for linters/formatters requires more effort to override 
   the defaults.

Estimated cost: Small

## Outcome

We chose to adhere to PEP8 with exceptions for line-wrapping and naming
convention. The team reviewed the line-wrapping options in the
aforementioned pull request and unanimously decided 99 characters was
preferable. Changing the naming scheme to PEP8 conventions would be a
lot of work and may look out of place when adopted into a mixed
Python/C++ codebase.


