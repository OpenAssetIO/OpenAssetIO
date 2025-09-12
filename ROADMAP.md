# Roadmap

The OpenAssetIO project has reached a stable v1 release of the core API.

However, there are still several features planned for the core API, and
the broader ecosystem remains at in a broadly beta-level state of
maturity.

This roadmap is influenced by community prioritisation exercises. The
results of which are available
[here](https://docs.google.com/spreadsheets/d/1ARGfLIbBg58rGTAgjcvr9DbmsXKTdQKO3BC_M3RQ_w4/edit#gid=0).

## Milestones

Each project in the OpenAssetIO ecosystem makes use of GitHub milestones
to track proposed features and their release targets.

Features and other improvements are placed into a SemVer-labeled
milestone based on a combination of priority and how breaking the change
is likely to be (see the
[versioning strategy](./README.md#versioning-strategy)).

Links to the milestones for various projects can be found below.

* [OpenAssetIO](https://github.com/OpenAssetIO/OpenAssetIO/milestones)
* [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation/milestones)
* [TraitGen](https://github.com/OpenAssetIO/OpenAssetIO-TraitGen/milestones)
* [usdOpenAssetIOResolver](https://github.com/OpenAssetIO/usdOpenAssetIOResolver/milestones)
* [OpenAssetIO-Manager-BAL](https://github.com/OpenAssetIO/OpenAssetIO-Manager-BAL/milestones)

## Current status

The core OpenAssetIO API has reached a stable v1 release.

The API is available in both C++ and Python and is designed to support
dual-language hosts.

The core API supports asset resolution, publishing, and relationships
via _entity references_.

The manager plugin system supports Python and C++ and hybrid Python/C++
plugins, configured either programmatically or through a TOML
configuration file, along with environment variables.

OpenAssetIO additionally supports UI delegation through a separate
plugin system. Participating hosts may allow asset managers to replace
elements of their UI. A typical example is to present an asset browser
in place of a file browser.

Information is carried across the API as OpenAssetIO _traits_. This
system has proven popular and effective. The OpenAssetIO-MediaCreation
repository contains community-defined traits providing categories/tags
and metadata for common VFX entities. They will continuously expand to
cover broader use cases as they arise.

The ecosystem of known host applications and manager plugins can be
found in the [examples](./examples/README.md) doc.

## Future plans - 2025/2026

The priority is now to encourage adoption and solicit feedback.

Despite the longer-term benefits that would be realised, early-adopters
on the *host* side are faced with a leap of faith if there is limited
manager support, and likewise *asset managers*/*studios* may also face
this leap of faith if there is limited host support.

Part of the project plan is therefore to lower these barriers for
early-adopters by providing more official integrations and integration
examples, whether directly on the project or via collaboration.

In parallel, the main development focus for the various OpenAssetIO
projects is to achieve their v1.0.0 release milestone. See the
milestones (above) for details.
