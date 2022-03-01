# The Basic Asset Library (BAL) example manager

The BasicAssetLibrary provides a basic "librarian" asset management
system.

It serves to provide a minimum level of functionality to allow simple,
repeatable demonstrations and end-to-end tests to be realized with as
little supporting infrastructure as possible.

It is not intended to be any kind of comprehensive example of the
breadth of functionality exposed though the OpenAssetIO API.
See the SampleAssetManager for a more concrete example of canonical
manager behavior.

> Note: This code is a sketch to facilitate testing and sample
> workflows. It should never be considered in any way a "good example
> of how to write an asset management system". Consequently, it omits
> a plethora of "good engineering practice".

## Features

-   Resolves references with the `bal://` prefix to data from a
    pre-configured library of assets stored in a `.json` file.

-   The library file to be used is controlled by the `library_path`
    setting, and this should point to a library file with valid content.

-   If no `library_path` has been specified, the `BAL_LIBRARY_PATH` env
    var will be checked to see if it points to a valid library file.

## Installation

Place the `plugin` subdirectory on `$OPENASSETIO_PLUGIN_PATH` and
configure an OpenAssetIO session to use the manager with the identifier:
`org.openassetio.examples.manager.bal`.

## Library file format

A [JSON Schema](https://json-schema.org) is provided [here](schema.json)
that validates a BAL library file.
