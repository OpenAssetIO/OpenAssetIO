# Contributing

This project operates a Pull Request model, using the [GitHub flow](https://guides.github.com/introduction/flow/index.html)
approach. The rough outline is as follows:

1. Chat with the Trusted Committers and community to define the scope of
   work
2. Fork the repo, and work in a branch
3. Create a Pull Request for Code Review
4. Address any comments
5. Work is merged

The main aim of the process is to keep people in the loop - avoiding any
surprises later on. This helps avoid churn/frustration for all involved.

More details on the development process will be provided soon. In the
meantime, please open an Issue or contact one of the Trusted Committers.

## Contribution sign off

OpenAssetIO is licensed under the [Apache 2.0 license](LICENSE). All
contributions to the project must abide by that license.

Contributions to OpenAssetIO require the use of the [Developer’s Certificate of Origin 1.1 (DCO)](https://developercertificate.org).
All commits must be signed-off as follows, before merge, to indicate
that the submitter accepts the DCO:

```
Signed-off-by: Jóna Jónsdóttir <jona.jonsdottir@example.com>
```

This can be added automatically to a commit using `git commit -s`.

In addition, contributors are required to complete either the Individual
or Corporate Contribution License Agreement. Please contact one of the
trusted committers for more information.

## Code style

For Python code we aim to adhere to the PEP8 convention, with a few
exceptions. Of these exceptions, the most obvious is that the naming
scheme is designed to more closely mirror our C++ naming conventions,
to ease C++ interop implementation and readability.

### Line wrapping

Line wrapping is performed at 99 characters for code, and 72 characters
for docstrings.

For markdown documents, line wrapping is also performed at 72
characters, where possible.

### Example code

An exception to the above is for code examples written in Python. Here,
PEP8 should be strictly followed, including its naming conventions.

### Method/function naming

Accessor (getter) methods that do not have a corresponding mutator
(setter) method at the same or higher access level (e.g. public getter
vs. private setter) _should not_ be prefixed with `get`.

If a getter does have a corresponding setter at the same or higher
access level (e.g. protected getter vs. public setter), then they
_should_ be prefixed with `get` and `set`, respectively.

This makes it easier to determine the API surface at a glance.

### Test cases

Where feasible, Python unit test cases should use a class for each unit,
where the methods of the test class are the test cases for that unit. In
addition, test cases should ideally be written using `when` and `then`
to delineate action/input and postcondition. The name of the test class
itself should begin with `Test_`. For example,

```python
class Test_UnitName:
    def test_when_action_then_postcondition(self, ...):
        ...
```

Often the unit under test is a class method, in which case the test
class name should include the method under test preceded by its class, 
separated by an underscore. For example,

```python
class Test_ManagerInterface_entityVersionName:
    ...
```

Don't be afraid of long test case names (up to the 99 character line 
length limit).

Sometimes the test is trivial, in that the unit is small and only has 
one code path. In that case shoehorning a test case description into a 
`when`/`then` style may be less readable than a simpler ad-hoc 
alternative. Best judgement should be used, bearing in mind readability
and consistency tradeoffs.

### IDE configuration

To aid in conforming to our coding style a [`.editorconfig`](https://editorconfig.org/)
file is included in the root of the repository, which has wide support
across various IDEs. For supported IDEs this config file can override
the default settings for inspections and formatting refactors.

In particular, more granular settings are included for IntelliJ-based
IDEs (for example, PyCharm) via the `ij_*` extensions.

Common file types that we expect to encounter during development of
OpenAssetIO have their own settings, many of which remain commented out
for reference and may be enabled and tweaked in future.

### Environment variables

All environment variables should be prefixed with `OPENASSETIO_`.
For example, `OPENASSETIO_LOGGING_SEVERITY`.

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment
Variable List_ page of the generated documentation.

## Trusted Committers

### Foundry
- @foundrytom [tom@foundry.com](mailto:tom@foundry.com)
- @feltech
