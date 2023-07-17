# Roadmap

The OpenAssetIO project is working towards an initial beta release of
the core API.

We are looking for early adopters who can help fine tune its final form,
and validate key design choices, and help flesh out asset types and
their properties.

The project is functional, and moving forward we expect minimal churn in
the API itself as we complete the implementation of language specific
features.

## Y23 Q3: v1.0.0b1

This release will support resolution and publishing of entities in batch
and interactive context, along with relationship discovery.

**Hosts:** C++, Python
**Managers:** Python

- [x] Migration to the [Trait based API](https://github.com/OpenAssetIO/OpenAssetIO/blob/main/doc/decisions/DR007-Hierarchical-or-compositional-traits-for-specifications.md).
- [x] Migration to batch-centric API.
- [ ] Migration of core API methods to C+. [In progress]
- [ ] Sundry breaking changes and tech-debt cleanup.

## Y24 Q1: v1.0.0

This release will provide additional introspection methods and
debugging functionality, along with language parity between Hosts and
Managers.

**Hosts:** C++, Python
**Managers:** C++, Python

- [ ] Auth related error codes.
- [ ] Debug trace logging support.
- [ ] Entity introspection API methods.
- [ ] C++ Plugin System
- [ ] Hybrid C++/Python manager bridge.
- [ ] Out-of-process Python
- [ ] Migrate landing page/examples to [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation)

## Y24 H1: OpenAssetIO UI v1.0.0a1

An initial release of the UI delegation layer that sits on top of
OpenAssetIO, allowing custom Manager UI elements to be directly embedded
into Host application.

This first stage will be limited to supporting integrations within a Qt
host.

## Y24 onwards

- Entity change notification/tracking.
- Out-the-box caching mechanisms for resolve.
- C API for FFIs or compiler isolation.
- Advanced workflow topics:
  - Transactions
  - Permissions
