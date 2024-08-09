# Sandboxed builds

For convenience, OpenAssetIO provides two different sandboxed build
environments.

## Docker

A simple way to perform a from-source build is to use the
[openassetio-build docker image.](https://github.com/OpenAssetIO/OpenAssetIO/pkgs/container/openassetio-build)

The `openassetio-build` image is almost identical to the
[ASWF CY24 Docker image](https://hub.docker.com/r/aswf/ci-base/tags?name=2024),
with just a few [added dependencies](BUILDING.md#library-dependencies).
This image contains all the necessary dependencies to build and test
OpenAssetIO, and functions as a fully configured build environment.

For example, to build and install OpenAssetIO (by default
to a `dist` directory under the build directory) via a container, from
the repository root run

```shell
docker run -v `pwd`:/src ghcr.io/openassetio/openassetio-build bash -c '
  cd /src && \
  cmake -S . -B build && \
  cmake --build build && \
  cmake --install build'
```

The install tree (`build/dist`) will contain a complete bundle, including the
core C++ shared library, Python extension module (which dynamically
links to the core C++ library) and Python sources.

The created bundle is therefore suitable for use in both C++ and Python
applications.

The docker image also comes with the [test dependencies](BUILDING.md#test-dependencies)
installed. To build and run tests, from the root of the repository run

```shell
docker run -v `pwd`:/src ghcr.io/openassetio/openassetio-build bash -c '
  cd /src && \
  cmake -S . -B build -DOPENASSETIO_ENABLE_TESTS=ON && \
  ctest --test-dir build'
```

> **Note**
>
> Running tests via `ctest` will automatically perform the build and
> install steps.

## Steps for creating openassetio-build docker image

The `openassetio-build` docker container is published to
`ghcr.io/openassetio/openassetio-build`. On occasion, it may become
necessary for contributors to rebuild and republish this image, find
instructions on how to accomplish this below.

### Building the image

OpenAssetIO provides a [makefile](../resources/build/Makefile)
to build the docker container. From `resources/build`, run

``` shell
make docker-image
```

> **Note**
>
> If you find you need to update the version, this can be found inside
> the makefile itself. The `openassetio-build` container is versioned
> according to the VFX reference platform versioning scheme, eg `2022.1`
> for version 1 of the `CY2022` based image.
>

### Deploying the image

To deploy the image, again from `resources/build`, we use `make`.

```shell
GITHUB_PAT=<token> GITHUB_USERNAME=<username> make publish-docker
```

`GITHUB_PAT` refers to a [personal access token](https://github.com/settings/tokens).
It must have the `wite:packages` permission.

> **Note**
>
> If this is a new image, the first time the image is published
> it will be created `private`. You can change the visibility through
> the GitHub web page for the package.
