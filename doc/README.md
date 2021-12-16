# OpenAssetIO Documentation

The OpenAssetIO docs are currently built with Doxygen - chosen as it is
the simplest solution for a mixed Python and C++ project.

They make use of [doxypy](https://github.com/0xCAFEBABE/doxypy) to
better document Python code with docstrings containing Doxygen
[commands](https://www.doxygen.nl/manual/commands.html). The main
limitation right now is the duplication of the namespace for hoisted
Python classes.

## Building via Docker

The simplest way to build the documentation is via Docker:

```
docker build . -t openassetio-doc-build
docker run -v `pwd`/../:/src openassetio-doc-build bash -c 'make -C /src/doc html'
```

If you have GNU Make installed on your system, the included `Makefile`
simplifies this to `make`.

The documentation will be build in the container, but stored (along with
the required additional tooling) in your local checkout - see
`html/index.html`.

## Building manually

If Docker is not available, you can build the documentation locally, but
there are a number of dependencies that must first be installed, and
available on `$PATH`:

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

Regardless of which mechanism you use, the resulting docs bundle will be
created in a `html` folder in this directory.  You can view the main
index page via `html/index.html`.

## Deploying the docs

Public facing documentation is served via GitHub Pages from the `docs`
branch of [TheFoundryVisionmongers/OpenAssetIO](https://github.com/TheFoundryVisionmongers/OpenAssetIO).
This is automatically deployed whenever the `main` branch of the repository
is pushed via GitHub Actions (see [workflows/docs.yml](../.github/workflows/docs.yml)).

### Manual deployment

Should GitHub Actions be unavailable, the deployment can be updated
manually, using the standard Pull Request process.

Specifically,
1. Check out the latest `main` branch.
2. Generate the documentation (see above), resulting in a `html`
   directory.
3. Check out the latest `docs` branch.
4. Replace the `docs` directory in the `docs` branch checkout with
   the generated `html` directory (i.e. renamed to `docs`).
5. Commit and push the updated `docs` branch to your fork of the
   repository, placing the (short) commit hash that the documentation
   was generated from in the commit message.
6. Create a Pull Request against the `docs` branch in the main
   repository.

For convenience, much of this can be automated using the `deploy`
target of the included `Makefile`, i.e.
```shell
make deploy
```
which will commit a previously generated `html` directory to a `docs`
directory in the `docs` branch, then push that branch to `origin`.

## Tidying up

Running `make clean` will remove any generated docs or automatically
installed tooling.

## Future work

Once the repository is stable, we will need to publish to a release
version subdirectory in the repository, so that documentation remains
available for older stable versions. This will necessitate changes to
the landing page to perform the appropriate redirect to the latest
documentation (and ideally offer a dropdown to switch versions).
