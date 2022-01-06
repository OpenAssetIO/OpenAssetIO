# Plugin System Test Resources

This directory contains resources for the plugin system tests.

## pathA, pathB, pathC, symlinkPath

These sub-directories contain minimal implementations of two
`PluginSystemPlugins`:

- `PackagePlugin` : A plugin implemented in a python package.
- `ModulePlugin` A plugin implemented in a single-file python module.

`PackagePlugin` is only available via `pathB`, but `ModulePlugin`
is installed in both `pathA` and `pathC`.

`symlinkPath` exposes `pathA` and `pathB` plugins via symlinks.

These permutations allow path precedence and traversal behaviors
to be properly tested.
