# Examples

There is an ever-growing list of example OpenAssetIO hosts and manager
plugins. They cover a large range, including reference implementations,
testing utilities, proof of concepts, and production integrations.

## This repository

In this repository you can find simple examples of host applications
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

### Jupyter notebooks

An ever-expanding collection of [Jupyter](https://jupyter.org/)
notebooks is available as
[examples in the MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation/tree/main/examples)
repository. These demonstrate core OpenAssetIO concepts alongside the
wider ecosystem, in particular as it relates to the VFX and media
creation industry, through executable Python snippets. The pre-rendered
notebooks can be viewed directly in GitHub, so downloading to execute
locally is not required.

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

### ComyUI OpenAssetIO nodes

The [ComfyUI plugin](https://github.com/OpenAssetIO/OpenAssetIO-ComfyUI)
adds custom nodes for ingest and publishing of assets via OpenAssetIO
entity references, rather than file paths.

## External projects

### Nuke

[Nuke](https://www.foundry.com/products/nuke-family/nuke) is the
industry-leading commercial compositing tool by Foundry. As of
version [15.1](https://campaigns.foundry.com/products/nuke-family/whats-new),
Nuke has built-in support for OpenAssetIO as a headline feature.

### Katana AssetAPI shim plugin

[Katana](https://www.foundry.com/products/katana) is a commercial look
development and lighting tool by Foundry. It is natively asset-aware
through its AssetAPI, which inspired the design of OpenAssetIO. The
[KatanaOpenAssetIO](https://github.com/TheFoundryVisionmongers/KatanaOpenAssetIO)
project adapts the Katana AssetAPI to the OpenAssetIO API, allowing
OpenAssetIO manager plugins to be used within Katana.

### Ayon manager plugin

[Ayon by Ynput](https://ynput.io/ayon/) is an open source asset
management system that forms part of Ynput's pipeline-as-service
offering. Their
[manager plugin](https://github.com/ynput/ayon-openassetio-manager-plugin)
is available on GitHub.

### Ftrack manager plugin

[Ftrack Studio](https://www.ftrack.com/en/studio) is a commercial
production tracking and asset management system. They maintain a
[manager plugin](https://github.com/ftrackhq/ftrack-openassetio-manager)
on GitHub.

### Blender OpenAssetIO demo script

[Blender](https://www.blender.org/) is an open source 3D digital content
creation tool.

The [Blender relationships demo script](https://github.com/elliotcmorris/openassetio-relationships-blender)
adds UI elements to Blender that allow a user to load external geometry
from an asset management system, and pick alternative proxy
representations of that geometry by querying OpenAssetIO entity
relationships.
