# DR025 UI delegation plugin interface

- **Status:** Proposed
- **Impact:** High
- **Driver:** @feltech
- **Approver:** The OpenAssetIO Community
- **Due date:** 2024-08-12
- **Outcome:** Manager plugins and UI delegate plugins will be separate
  plugins with their own plugin systems. The UI delegate plugin will be
  provided a reference to the manager implementation.

## Background

OpenAssetIO is an abstraction that aims to be minimally opinionated.
Asset-managed pipelines don’t conform to a single structure — each
facility will vary in its workflow processes and backend systems, often
significantly. The OpenAssetIO core library provides an API for common
operations that a host application may wish to perform, with no
assumptions made about how that data is referenced or structured on the
backend.

However, some user-facing operations require knowledge of how a
particular pipeline works so that the appropriate interface can be shown
to the user.

For example, using a dedicated asset-centric browser UI, rather than
browsing for files on a file system, could provide a richer and more
relevant interface for artists, by filtering for approved assets that
are relevant for their current task, and presenting useful metadata.

A third-party vendor attempting to implement this in a generic way that
works across all potential pipeline setups is a daunting task, and it is
very unlikely to warrant expending engineering effort to do optimally
when it is far from the primary purpose of the software.

The engineers best placed to implement such an interface are the
maintainers of the asset management system itself. However, typically
this means separate secondary applications or, at best, surface-level
patching of application UIs, without deep integration into / replacement
of the existing UI layout.

If a third-party vendor can provide UI hooks into their software, such
that appropriate UI functionality can be _delegated_ to a plugin, then
we can have the best of both worlds — a native level integration of
bespoke interfaces that are optimized for the user's context.

### Aims

The aim of this decision is not to fully design the architecture for UI
delegation in OpenAssetIO. The aim is to decide on broad architecture,
with a focus on the fundamentals that must be fixed in place to enable
future evolution without requiring significant changes by host and
manager maintainers. That is, the primary focus is on the plugin
architecture and the (breaking) changes required to support it.

### Prior art

The precursors to OpenAssetIO provide some prior art in the area of UI
delegation.

#### Katana

[Katana](https://www.foundry.com/products/katana) is a look development
and lighting tool by Foundry, and its AssetAPI was the original
inspiration for OpenAssetIO. The AssetAPI and
[AssetWidgetDelegate](https://learn.foundry.com/katana/Content/tg/asset_management_system_plugin_api/extending_user_interface.html)
plugin architecture is battle tested and in use in production today.

Katana AssetAPI plugins must be written in C/C++, and the UI delegation
AssetWidgetDelegate plugin must be written in Python. Therefore, there
are two independent plugin systems, and the AssetWidgetDelegate plugin
is linked to the AssetAPI plugin only by a shared unique string
identifier.

The AssetWidgetDelegate plugin typically accesses the AssetAPI via a
global singleton and defines functions that provide or modify PyQt
widgets (Katana is Qt based). The plugin is expected to inherit from a
`BaseAssetWidgetDelegate` class and override methods that create or
modify specific types of widgets. For example, creating an asset
identifier inline control, or customizing an asset browser panel.

#### FnAssetAPI

FnAssetAPI was the direct ancestor of modern OpenAssetIO and was born
out of experience with Katana's AssetAPI by Foundry and its customers,
originally back in 2013. Development was in part a collaboration with
[Ftrack](https://www.ftrack.com/en/) - an off-the-shelf asset management
system for media creation. This culminated in a public demo showcasing a
native-level integration of Ftrack into Foundry's Hiero and Nuke at [NAB
2013](https://youtu.be/E1kpWC_pGbw?t=1212). Development of FnAssetAPI
continued for a while after, but was ultimately placed on hold, until
2021 when it formed the basis of OpenAssetIO.

FnAssetAPI was entirely Python-based for most of its life. C++
functionality was begun but not proven out, and the approach wasn’t
adopted for OpenAssetIO's C++ architecture.

The UI delegation layer of FnAssetAPI took a slightly different approach
to Katana. In FnAssetAPI, a single plugin system was used to load both
the `ManagerInterfaceBase`-derived core interface and a
`ManagerUIDelegate`-derived UI delegate. That is, a single plugin
exposed two factory functions, one for the core interface and one for
the UI delegate.

The UI delegate factory function required a pre-constructed interface as
an argument, thus avoiding the need for a global singleton to gain
access to the core plugin from the UI plugin. However, the host
application would request a UI delegate object through a global
singleton `Session` object.

The `ManagerUIDelegate` was expected to override methods that are
responsible for creating or modifying PySide widgets (again, Qt based),
much like Katana's `BaseAssetWidgetDelegate`. Since FnAssetAPI was meant
as a generic interface, the methods weren’t application-specific, being
limited to `getWidget` and `populateUI` functions, with method arguments
providing the context for which type of widget should be constructed.

## Options considered

### Option 1

An entirely separate UI delegate plugin, linked to the core plugin only
by unique identifier (Katana-style).

The UI delegate plugin provides a factory function for instantiating a
UI delegate object, which in turn is responsible for creating/modifying
UI elements.

The UI plugin system uses the same structure as the core plugin systems.
In particular, both C++ and Python plugins can be supported.

#### Pros

- Trivial to choose a different language (C++/Python) for the UI plugin
  vs. core plugin.
- Can add Python/C++ support first then add C++/Python support later.
- UI delegation functionality is invisible and unobtrusive if unused.
- Allows independent development, versioning and deployment of UI
  plugins and core plugins. A single core plugin may work across all
  applications, whereas a UI plugin may have a different variant for
  each framework (i.e. Qt vs. GTK vs. wxWidgets vs. FLTK ...) or even
  each application.
- Very few breaking changes required, if any.

#### Cons

- Extra boilerplate code for host applications and manager plugin
  authors.
- Additional deployment effort for facilities maintaining yet another
  plugin.
- Core and UI plugins maintained and versioned independently must
  be kept compatible and deployed in compatible pairs.
- The UI delegate may need access to the core manager plugin. The exact
  mechanism for this needs designing. E.g. use `Context.managerState`
  vs. inject `Manager` vs. inject `ManagerInterface`.

### Option 2

A single logical plugin using the existing plugin system, with
additional method(s) added to the existing `ManagerInterface` class.
I.e. a `getUIDelegate` (or similar) method returns a UI delegate object,
which is responsible for creating/modifying UI elements.

#### Pros

- Choosing a different language (C++/Python) for the UI vs. core methods
  is possible using the hybrid plugin system with the addition of a new
  `Capability` enum value for UI related API methods.
- Minimal additional boilerplate for host application and manager plugin
  authors.
- UI and core API implementations are compatible by construction.
- The UI layer has direct access to the private implementation of the
  core API plugin.

#### Cons

- Relying on the hybrid plugin system to provide multi-language support
  adds unnecessary boilerplate to the implementation of the plugin when
  its functionality is higher level than (and more akin to a consumer
  of) the core API.
- Relying on the hybrid plugin system means that support for UI
  delegation must be added to the C++ API first. So it is not possible
  to add Python support first and C++ support later.
- Definitely requires breaking changes (though only additions so should
  be source compatible).
- Tight coupling of UI and headless concerns means care must be taken,
  especially with regard to dependencies. Many use cases for OpenAssetIO
  are completely headless and don’t require UI functionality.
- Likely must maintain multiple builds of the same plugin with tweaks
  for different UI frameworks and/or applications, even if the core
  plugin API is stable.

## Outcome

We will pursue Option 1. Keeping the manager plugin and UI delegate
plugin separate has clear advantages in development and deployment,
given that there are likely to be far more variations of the UI
delegate plugin (to account for multiple UI frameworks/applications). A
separate UI delegate plugin system also emphasizes the optionality of
the component so as not to disenfranchise headless use-cases.

### Future work: Linking the two plugins

A key question is if, and how, the manager plugin and the UI delegate
plugin should be connected. There are few options here that must be
explored in future work.

* It may be that the two plugins can operate entirely independently,
  without any communication or shared state between them.
* If there is communication between the plugins, that could be viewed
  as an implementation detail of the plugin authors, and OpenAssetIO
  can treat them as independent.
* The UI delegate might only need access to the public API surface area,
  effectively acting as another host application component. In this
  case, perhaps it's useful and sufficient to inject the host-facing
  `Manager` middleware into the UI delegate during initialisation.
* If the UI delegate requires full access to the private implementation
  of the manager plugin, additional API changes may be necessary to
  expose the underlying `ManagerInterface` so that it can be injected
  into the UI delegate during initialisation.

All these scenarios have their own limitations and complications.

However, perhaps the purest OpenAssetIO way of sharing state is via the
`Context`. All API methods take a `Context` object. These objects
contain an opaque state object `managerState` provided by the underlying
plugin (see `ManagerInterface.createState(...)`). It is the primary
mechanism that allows patterns of idempotency, serialisation, and
distributed processing in OpenAssetIO.

The `Context.managerState` could also be used to allow the manager
plugin and UI delegate plugin to share state and communicate. The
manager plugin authors are free to put whatever they want in the
`managerState` - e.g. it could be a reference to the `ManagerInterface`
implementation itself, or a shared cache, persistent network connection,
etc.
