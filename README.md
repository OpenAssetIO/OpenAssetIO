# OpenAssetIO

An open-source interoperability standard for tools and content
management systems used in media production.

It aims to reduce the integration effort and maintenance overhead of
modern CGI pipelines, and pioneer new, standardized asset-centric
workflows in content creation tooling.

## Problem statement summary

In modern creative pipelines, data is often managed by an authoritative
system (Asset Management System, Digital Asset Manager, MAM, et. al).

It is common for media creation tools to reference this managed data by
its present location in a file system.

This not only limits document portability, but strips semantically
meaningful information about the identity, purpose or heritage of the
data - complicating topics such as loading, version management and
distributed computation.

Common workarounds to the restrictions associated with path-based
referencing can be fragile and require on-going maintenance as tools and
workflows evolve.

## What OpenAssetIO provides

OpenAssetIO enables tools to reference managed data by identity (using
an "Entity Reference") instead of a file system path.

This allows for any properties of the entity (such as its location or
available versions) to be "resolved" on demand, taking into account the
current compute environment.

This is achieved through the definition of a common set of interactions
between a host of the API (eg: a Digital Content Creation tool or
pipeline script) and an Asset Management System (or DAM, MAM, etc.).

This common API surface area hopes to remove the need for common
pipeline business logic to be re-implemented against the native API of
each tool, and allows the tools themselves to design new workflows
that streamline the creation of complex assets.

OpenAssetIO enabled tools and asset management systems can freely
communicate with each other, without needing to know any specifics of
their respective implementations.

OpenAssetIO is not unique in the ability to resolve identifiers, but it
is the first to offer an industry-wide, truly open standard that can be
used in any relevant tool or application.

## Scope

The API has no inherent functionality. It exists as a bridge - at the
boundary between a process that consumes or produces data (the host),
and the systems that provide data coordination and version management
functionality.

The API covers the following areas:

- Resolution of asset references (URIs) into a dictionary of data,
  grouped into one or more "traits" (providing URLs for access, and
  other asset data).
- Publishing data for file-based and non-file-based assets.
- Discovery and registration of related assets.
- Replacement/augmentation of in-application UI elements such as
  browsers and other panels/controls.

The API, by design, does not:

- Define any standardized data structures for the storage or
  description of assets or asset hierarchies.
- Dictate any aspect of how an asset management system operates,
  organizes, locates or manages asset data and versions.

The API builds upon the production-tested [Katana Asset API](https://learn.foundry.com/katana/4.0/Content/tg/asset_management_system_plugin_api/asset_management_system.html),
addressing several common integration challenges and adding support
for a wider range of asset types and publishing workflows.

## API documentation

The documentation for OpenAssetIO can be found here: [https://openassetio.github.io/OpenAssetIO](https://openassetio.github.io/OpenAssetIO/).

## Project status

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6046/badge)](https://bestpractices.coreinfrastructure.org/projects/6046)

> **Important:** The project is currently in early beta stage and is
> subject to change. Do not deploy the API in production critical
> situations without careful thought.

We are currently working towards a v1.0.0 release. We are in the process
of porting the core API from Python to C/C++.

The code is presented here in its current form to facilitate discussion
and early-adopter testing. We actively encourage engagement in the
[discussion](https://github.com/OpenAssetIO/OpenAssetIO/discussions)
and to give feedback on current [Issues](https://github.com/OpenAssetIO/OpenAssetIO/issues)
and [Pull Requests](https://github.com/OpenAssetIO/OpenAssetIO/pulls).

We have been making some structural changes whilst migrating to this
repository and removing some spurious/legacy concepts. There may well
be some rough edges so bear with us whilst we get things ship-shape.

Please see the [project board](https://github.com/orgs/OpenAssetIO/projects/1)
for work in progress, as well as up-coming topics.

### TODO list

- Complete core C/C++ API work
- Define Traits for post-production in the [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation)
  repository
- [AR2.0](https://graphics.pixar.com/usd/docs/668045551.html) interop
  investigations
- Katana Asset API migration guide/shims

## Background

Within the Media and Entertainment sector, digital content (such as
images, models and editorial data) is usually managed by a central
catalog. This catalog is commonly known as an "Asset Management System",
and forms a singular source of truth for a project.

OpenAssetIO provides an abstraction layer that generalizes the dialog
between a 'host' (eg. a Digital Content Creation application such as
Maya&reg; or Nuke) and one of these systems - a 'manager' (eg. ShotGrid,
ftrack or other proprietary systems).

This project first began in 2013, taking inspiration from the production
tested [Katana Asset API](https://learn.foundry.com/katana/4.0/Content/tg/asset_management_system_plugin_api/asset_management_system.html)
to make it more suitable for a wider variety of uses. Modern pipelines
are incredibly nuanced. Finding a common framework that brings value in
this space is challenging to say the least. Prototypes built during the
development of `OpenAssetIO` over the last few years have demonstrated
significant developer and artist value.

We hope the API forms a practical starting point that addresses many
real-world use cases, and as an industry, we can evolve the standard
over time to support any additional requirements. We are currently
investigating the relationship with [Ar 2.0](https://graphics.pixar.com/usd/docs/668045551.html),
which appears to overlap with a subset of `OpenAssetIO`s concerns.

## Getting started

### Installation

The OpenAssetIO codebase is available as a git repository on GitHub

```shell
git clone git@github.com:OpenAssetIO/OpenAssetIO
```

### System requirements

Linux is currently the only fully tested platform. Support
for other platforms is the subject of ongoing work.

#### Quick start: Using the ASWF Docker image

The Academy Software Foundation maintains a set of VFX Reference
Platform compatible [Docker](https://www.docker.com/) images [here](https://github.com/AcademySoftwareFoundation/aswf-docker).

The CY22 image contains all dependencies currently required for building
OpenAssetIO. For example, to build and install the C/C++ component of
OpenAssetIO (by default  to a `dist` directory under the build
directory) via a container, from the repository root run

```shell
docker run -v `pwd`:/src aswf/ci-base:2022.2 bash -c '
  cd /src && \
  cmake -S . -B build && \
  cmake --build build && \
  cmake --install build'
```

#### Other build methods

For detailed instructions see [BUILDING](BUILDING.md).

## Getting involved

- See the [contribution guide](contributing/PROCESS.md)
- Join our [working group](https://github.com/OpenAssetIO/OpenAssetIO-WG) meetings

> Maya&reg;, is a registered trademark of Autodesk, Inc., and/or its
> subsidiaries and/or affiliates in the USA and/or other countries.
