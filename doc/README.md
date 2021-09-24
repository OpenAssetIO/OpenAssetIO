# OpenAssetIO Documentation

The OAIO docs are currently built with Doxygen - chosen as it is the
simplest solution for a mixed Python and C++ project.

They make use of [doxypy](https://github.com/0xCAFEBABE/doxypy) to
better document Python code with docstrings containing Doxygen
[commands](https://www.doxygen.nl/manual/commands.html). The main
limitation right now is the duplication of the namespace for hoisted
Python classes.

## Building

To build the documentation there are a number of dependencies that must
first be installed, and available on `$PATH`:

- [GNU Make](https://www.gnu.org/software/make/)
- [Doxygen](https://www.doxygen.nl) 1.8.11 (exact version, see [this
  issue](https://github.com/doxygen/doxygen/issues/7096))
- [npm](https://nodejs.org/en/)

Once `doxygen` and `npm` are available on `$PATH`, the included
`Makefile` will build the docs bundle, simply run:

```
make html
```

The `Makefile` takes care of installing the other pre-requisite tooling
such as `sass` and `doxypy.py` for you.

## Viewing the docs

The resulting docs bundle will be created in a `html` folder in this
directory.  You can view the main index page via `html/index.html`.

## Tidying up

Running `make clean` will remove any generated docs or automatically
installed tooling.

