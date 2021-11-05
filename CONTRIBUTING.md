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

## Code style

For Python code we aim to adhere to the PEP8 convention, with a few
exceptions. Of these exceptions, the most obvious is that the naming
scheme is designed to more closely mirror our C++ naming conventions,
to ease C++ interop implementation and readability.

Line wrapping is performed at 99 characters for code, and 72 characters
for docstrings.

For markdown documents, line wrapping is also performed at 72
characters, where possible.

### Example code

An exception to the above is for code examples written in Python. Here,
PEP8 should be strictly followed, including it's naming conventions.

### IDE configuration

To aid in conforming to our coding style a [`.editorconfig`](https://editorconfig.org/)
file is included in the root of the repository, which has wide support
across various IDEs. For supported IDEs this config file can override
the default settings for inspections and formatting refactors.

In particular, more granular settings are included for IntelliJ-based
IDEs (for example, PyCharm) via the `ij_*` extensions.

Common file types that we expect to encounter during development of OAIO
have their own settings, many of which remain commented out for
reference and may be enabled and tweaked in future.

### Environment variables

All environment variables should be prefixed with `OAIO_`. For example,
`OAIO_LOGGING_SEVERITY`. 

When documenting environment variables in docstrings or doxygen comment
blocks, precede the variable name with the `@envvar` tag, which will
cause the variable and its description to be listed in the _Environment 
Variable List_ page of the generated documentation.

## Trusted Committers

### Foundry
- @foundrytom
- @feltech
- @fn-yves
- @TomFoundry
