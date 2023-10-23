# Roadmap

The OpenAssetIO project is working towards an initial beta release of
the core API.

We are looking for early adopters who can help fine tune its final form,
and validate key design choices, and help flesh out asset types and
their properties.

The project is functional, and moving forward we expect minimal churn in
the API itself as we complete the implementation of language specific
features.

This roadmap is influenced by community prioritisation exercises. The
results of which are available
[here](https://docs.google.com/spreadsheets/d/1ARGfLIbBg58rGTAgjcvr9DbmsXKTdQKO3BC_M3RQ_w4/edit#gid=0).

## Y23 Q3: v1.0.0b1

**Released October 27th**

Milestone: [here](https://github.com/OpenAssetIO/OpenAssetIO/milestone/1)

This release will support resolution and publishing of entities in batch
and interactive context, along with relationship discovery.

**Hosts:** C++, Python
**Managers:** Python

- [x] Migration to the [Trait based API](https://github.com/OpenAssetIO/OpenAssetIO/blob/main/doc/decisions/DR007-Hierarchical-or-compositional-traits-for-specifications.md).
- [x] Migration to batch-centric API.
- [x] Migration of core API methods to C++.
- [x] Sundry breaking changes and tech-debt cleanup.

## Y24 Q1: v1.0.0

**Backlog:** [here](https://github.com/OpenAssetIO/OpenAssetIO/milestone/7)

This release will provide additional introspection methods and
debugging functionality, along with language parity between Hosts and
Managers.

**Hosts:** C++, Python
**Managers:** C++, Python

- [ ] Debug trace logging support.
- [ ] Entity introspection API methods.
- [ ] C++ Plugin System
- [ ] Hybrid C++/Python manager bridge.
- [ ] Read-through cache mix-ins.
- [ ] Migrate landing page/examples to [OpenAssetIO-MediaCreation](https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation)

## Y24 onwards

- UI Layer
- Auth related error codes.
- Entity change notification/tracking.
- C API for FFIs or compiler isolation.
- Out-of-process Python
- Advanced workflow topics:
  - Transactions
  - Permissions
