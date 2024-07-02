# Examples

As part of the ecosystem there is an ever-growing list of example
OpenAssetIO hosts and manager plugins. They cover a large range,
including reference implementations, testing utilities, proof of
concepts, and production integrations.

## This repository

In this directory you can find simple examples of host applications
and manager plugins that make use of OpenAssetIO.

### Hosts

#### simpleResolver

The [simpleResolver](host/simpleResolver/README.md) is a Python
command-line tool that can take an entity reference and a list of
trait IDs, `resolve` them, and present the results as a dictionary
in the terminal.

### Managers

#### SimpleCppManager

The [SimpleCppManager](manager/SimpleCppManager/README.md) is a C++
OpenAssetIO manager plugin that provides functionality for a limited
cross-section of the OpenAssetIO API. Its "database" of entities is
taken directly from the settings provided by the host. It is designed to
be used for testing C++ plugin support in host applications.

## Other OpenAssetIO projects

### Python manager plugin template

The [Python manager plugin template](https://github.com/OpenAssetIO/Template-OpenAssetIO-Manager-Python)
provides a documentation-by-example implementation of a Python manager
plugin.

### Basic Asset Library

The [Basic Asset Library
(BAL)](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL) is a
Python OpenAssetIO manager and plugin that is designed to enable host
applications to test their integration against a wide spectrum of
possible asset management system archetypes. It is designed to be fully
puppetable, with responses controlled by a JSON configuration file. BAL
is used extensively by the team for internal testing and demos of
OpenAssetIO. Note that it is not intended as a reference implementation.

### USD Ar2 shim plugin

The [USD Asset Resolver plugin](https://github.com/OpenAssetIO/usdOpenAssetIOResolver#readme)
allows OpenAssetIO plugins to be used within the USD ecosystem, by
adapting the Ar2 API to the OpenAssetIO API.

### OpenTimelineIO media linker plugin

The [OTIO media linker](https://github.com/OpenAssetIO/otio-openassetio)
plugin allows OpenAssetIO entity references to be recognised within
OTIO documents, and resolved to their file path when the document is
loaded.

## External projects

### Nuke

[Nuke](https://www.foundry.com/products/nuke-family/nuke) is the
industry-leading commercial compositing tool by Foundry. As of
version [15.1](https://campaigns.foundry.com/products/nuke-family/whats-new),
Nuke has built-in support for OpenAssetIO as a headline feature.


### Ayon manager plugin

[Ayon by Ynput](https://ynput.io/ayon/) is an open source asset
management system that forms part of Ynput's pipeline-as-service
offering. Their [manager plugin](https://github.com/ynput/ayon-openassetio-manager-plugin)
is available on GitHub.

### Blender OpenAssetIO demo script

[Blender](https://www.blender.org/) is an open source 3D digital content
creation tool.

The [Blender relationships demo script](https://github.com/elliotcmorris/openassetio-relationships-blender)
adds UI elements to Blender that allow a user to load external geometry
from an asset management system, and pick alternative proxy
representations of that geometry by querying OpenAssetIO entity
relationships.
