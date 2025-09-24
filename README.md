# OpenAssetIO

An open-source interoperability standard for tools and content
management systems used in media production.

It aims to reduce the integration effort and maintenance overhead of
modern CGI pipelines, and pioneer new, standardized asset-centric
workflows in content creation tooling.

> - 👋 Come chat with us on [ASWF Slack](https://academysoftwarefdn.slack.com/archives/C03Q36QS8N4)
>   or our [mailing list](https://lists.aswf.io/g/openassetio-discussion).
> - 🧰 Get started with the [API docs](https://docs.openassetio.org/OpenAssetIO),
>   Manager plugin [template](https://github.com/OpenAssetIO/Template-OpenAssetIO-Manager-Python),
>   and [MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation#readme)
>   for post-production workflows.
> - 📖 Or see some [examples](examples/README.md) in the OpenAssetIO
>   ecosystem.
> - 👀 You can follow the development effort [here](https://github.com/orgs/OpenAssetIO/projects/1/views/7)
>   and the longer term roadmap [here](ROADMAP.md).

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

The documentation for OpenAssetIO can be found here: [https://docs.openassetio.org/OpenAssetIO](https://docs.openassetio.org/OpenAssetIO/).

## Project status

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6046/badge)](https://bestpractices.coreinfrastructure.org/projects/6046)

Roadmap details can be found [here](ROADMAP.md).

We actively encourage engagement in the project. See various ways to
get in touch [here](SUPPORT.md).

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
this space is challenging to say the least. Prototypes and early
production use of `OpenAssetIO` over the last few years have
demonstrated significant developer and artist value.

For example, referencing assets by identity instead of path makes
documents more portable and dynamic - identity is not platform specific
and can change over time ("vLatest"); and additional metadata carried
alongside (or instead of) a path allows DCC parameters to be driven
by the asset management system (e.g. an image's colour space);
publishing through an asset management system then allows the pipeline
a chance to properly ingest assets - such as versioning and making
available for review.

We hope the API forms a practical starting point that addresses many
real-world use cases, and as an industry, we can evolve the standard
over time to support any additional requirements.

## Getting started

### System requirements

OpenAssetIO aligns itself with [VFX Reference Platform CY2024](https://vfxplatform.com/).

Windows, macOS, and Linux are all supported platforms.

### Getting OpenAssetIO

OpenAssetIO can be used either as a Python package, or as a C++ package
with optional Python bindings.

> **Note**
> Currently, to create non-Python host integrations or manager plugins,
> one must [build from source](doc/BUILDING.md#building).

For pure Python projects, OpenAssetIO is available on PyPI, simply run:

> **Warning**
> PyPI releases are currently `x86_64` binary only (no `sdist`). If you
> are on an ARM based machine (e.g. Apple Silicon), then you will need
> to build locally or install an `x86_64` version of Python.

```bash
python -m pip install openassetio
```

You may also build all formulations of OpenAssetIO from source, in
various combinations and configurations.
For detailed instructions, see [building](doc/BUILDING.md).

## Getting involved

> **Note**
> Contributions are very welcome, though the following is important to
> bear in mind: Similarly to other ASWF projects, compatibility with
> other software in VFX pipelines is important, and so stability and
> reliability in the project is maintained by following strict
> standards. Making a start on contributing to the core library can be
> daunting at first. While the interfaces from a user perspective are
> straightforward to use, the core implementation detail is inherently
> abstract.

Contributions to the core tasks outlined in our [roadmap](ROADMAP.md)
would be very welcome.

If you're interested in the project, please [reach out](SUPPORT.md).
Also,

- See the [contribution guide](CONTRIBUTING.md)
- Join our [working group](https://github.com/OpenAssetIO/OpenAssetIO-WG)
  meetings

> Maya&reg;, is a registered trademark of Autodesk, Inc., and/or its
> subsidiaries and/or affiliates in the USA and/or other countries.

## Versioning strategy

OpenAssetIO broadly follows [semver](https://semver.org/). We maintain
a compatibility guarantee based on the category of release in question.

- Major releases : May contain source incompatible changes.
- Minor releases : May contain binary incompatible changes.
- Patch releases : Will remain compatible.

OpenAssetIO is a multi-language, multi-headed library, presenting
differing interface points for hosts and managers. These interfaces are
versioned together under a single OpenAssetIO version. For this reason,
it is possible that a breaking OpenAssetIO update may not cause an
incompatibility for your particular concern. For information on this,
consult the [release notes](./RELEASE_NOTES.md).

### Pre-releases

During pre-release phases, the project utilizes a reduced form of
semver, which looks like `v1.0.0-beta.x.y`.

During this period, one may assume that the `x` above is synonymous with
major version, and the `y` with minor version, for the purpose of
compatibility. This means patch versions will be rolled into minor
versions, but you may still consult the [release
notes](./RELEASE_NOTES.md) for specific compatibility information.
