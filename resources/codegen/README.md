# OpenAssetIO Code Generation Tool

The `openassetio-codegen` tool can be used to generate Trait and
Specification classes from a simple YAML description. This avoids
the laborious and error-prone task of creating these by hand.

This package is entirely self-contained and can be used without an
available `openassetio` installation. In fact, it is used by OpenAssetIO
itself to generate core Traits and Specifications.

It provides code generation CLI, along with a corresponding python
package that can be used for custom generation.

## Supported languages

- Python 3.7+

## Installation

```bash
python -m pip install .
```

## Usage

```bash
openassetio-codegen -h
```

## Development notes

This package follows the main [OpenAssetIO contribution process](../../contributing/PROCESS.md).

However, as a pure Python project, it adheres to strict PEP-8 naming
conventions.

### Running tests

We recommend using a suitably configured Python virtual environment for
all development work.

To run the project tests, first ensure that you have a working (and
version matched) `openassetio` installation available. Though the tool
itself has no runtime dependencies on `openassetio`, the tests verify
the functionality of the auto generated code. Consequently, they need to
import `openassetio` for the various base and data classes.

See the `openassetio` [README.md](../../README.md) for instructions on
how to build and install the core API itself.

Once this is done, you can then install the prerequisite toolchain
(`pytest`), create an editable installation of the package, and run the
tests:

```bash
python -m pip install -r tests/requirements.txt
python -m pip install -e .
pytest
```
