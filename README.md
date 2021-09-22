# OpenAssetIO

An open-source interoperability standard for tools and content management systems used in media production.

OpenAssetIO enabled tools and systems can freely communicate with each other without needing to know any specifics of their respective implementations.

## Overview

Within the Media and Entertainment sector, digital content (such as images, models and editorial data) is usually managed by a central catalog. This catalog is commonly known as an "Asset Management System", and forms a singular source of truth for a project.

OpenAssetIO provides an abstraction layer that generalises the dialog between a 'host' (eg: a Digital Content Creation application such as Maya&reg; or Nuke) and one of these systems - a 'manager'.

## Project status

> **Important:** The project is currently in early beta stage and is subject to change. Do not deploy the API in production critical situations without careful thought.

This project first began in 2013, taking inspiration from the production tested [Katana AssetAPI](https://learn.foundry.com/test/katana/4.0/Content/tg/asset_management_system_plugin_api/asset_management_system.html) to make it more suitable for a wider variety of uses.

We are currently working towards a v1.0.0 release. At present, the API is implemented in pure `Python`, whilst some structural revisions are being made. Once the surface area has stabilised, the Core API will be ported to `c++` with bindings to `Python`.

The code is presented here in its current for to facilitate discussion and early-adopter testing. We actively encourage engagement in the [discussion](https://github.com/TheFoundryVisionmongers/OpenAssetIO/discussions) and to give feedback on current [Issues](https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues) and [Pull Requests](https://github.com/TheFoundryVisionmongers/OpenAssetIO/pulls).

We have been making some structural changes prior to migrating to this repository, updating from Python 2 to Python 3 and removing some legacy. There may well be some rough edges so bear with us whilst we get things ship-shape.

### TODO List
 - Migrate documentation
 - [AR2.0](https://graphics.pixar.com/usd/docs/668045551.html) interop investigations
 - Migrate `ManagerPlugin` test harness
 - Migrate example code
 - C++ port of Core API
 - Katana AssetAPI migration guide/shims

## Getting started

### System requirements
- `Python 3.7` or later

### Installation
```
git clone git@github.com:TheFoundryVisionmongers/OpenAssetIO
cd OpenAssetIO
python3.7 -m venv .venv
. .venv/bin/activate
pip install -e .
```

### Running tests
```
pip install -r tests/requirements.txt
pytest
```

## Getting involved
- See [CONTRIBUTING.md](CONTRIBUTING.md)


> Maya&reg;, is a registered trademark of Autodesk, Inc., and/or its subsidiaries and/or affiliates in the USA and/or other countries.
