# ABI change monitoring

When the OpenAssetIO C++ ABI changes, we need to know about it to inform
our release notes and SemVer versioning.

This is aided (though not solved!) by automated testing against a
snapshot dump of the ABI. The tool we use for this
is [libabigail](https://sourceware.org/libabigail/manual/libabigail-overview.html),
in particular its `abidiff` and `abidw` tools.

> **Note**
>
> The ABI on other platforms, including other Linux distributions, may
> (subtly) vary. Always generate a dump of a build from the same Docker
> image as is used on CI, i.e. `ghcr.io/openassetio/openassetio-build`.

If the ABI of an OpenAssetIO library changes, and the change is
unavoidable, then a new XML snapshot dump of the ABI must be created
(and release notes updated as appropriate).

To do this we use `abidw`. For convenience, the `openassetio-build`
Docker image has libabigail pre-installed.

The generated snapshot is then checked against new builds using
`abidiff`.

## Limitations

ABI checking via libabigail is not a panacea to determining the level of
change incompatibility. There are several cases where human detection of
breaking changes, affecting release notes and SemVer versioning, is
still required:

* The source or binary compatibility implications of a change detected
  by libabigail must be decided by a human. Many changes are
  non-breaking; and those that are must be categorised as a source or
  binary incompatibility, and whether the incompatibility affects the
  host interface or the manager interface, or both.
* There are rare cases where a source incompatibility does not imply
  binary incompatibility, and so libabiligail will not detect these
  cases.
* Changes to types/functions/variables defined exclusively in headers,
  and which are not used in an OpenAssetIO binary, will not be detected
  automatically.
* Changes to Python types/functions/variables will not be detected,
  including changes to C++ Python bindings.
* Workflow changes, where we change the expected usage pattern of the
  API, without changing the API itself, must be considered as a
  potential breaking change.

## Updating the ABI snapshot

Assuming:

* The current working directory is at the root of the repository.
* A POSIX host (for Docker invocation).
* The library with an ABI break is `libopenassetio`.

1. Create a new build using the `openassetio-build` Docker image

   ```sh
   docker run --rm -v $(pwd):/src \
       ghcr.io/openassetio/openassetio-build \
       bash -c 'cd /src && \
           cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug && \
           cmake --build build --parallel'
   ```

2. Generate a new XML formatted ABI dump to overwrite the existing XML
   dump under `resources/abi`

   ```sh
   docker run --rm -v $(pwd):/src \
       ghcr.io/openassetio/openassetio-build \
       abidw /src/build/lib64/libopenassetio.so.1.0.0 \
       > resources/abi/libopenassetio.so.1.0.0.xml
   ```

3. We can then check against this using `abidiff`

    ```sh
    docker run --rm -v $(pwd):/src \
        ghcr.io/openassetio/openassetio-build \
        abidiff /src/resources/abi/libopenassetio.so.1.0.0.xml \
        /src/build/lib64/libopenassetio.so.1.0.0
    ```

   or re-run the ABI tests via CTest

    ```sh
    docker run --rm -v $(pwd):/src \
       ghcr.io/openassetio/openassetio-build \
       bash -c 'cd /src && \
           cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug \
              -DOPENASSETIO_ENABLE_TESTS=ON \
              -DOPENASSETIO_ENABLE_TEST_ABI=ON && \
           ctest --test-dir build --output-on-failure \
              -R openassetio.test.abi'
    ```

4. Commit the new ABI dump alongside the changes that caused the ABI
   break. If this change causes source or binary incompatibility with
   the previous release, [update](../../doc/contributing/CHANGES.md) the
   [release notes](../../RELEASE_NOTES.md) based on the
   [versioning policy](../../README.md#versioning-strategy)
