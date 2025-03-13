# Plugin System Test Resources

This directory contains resources for the plugin system tests.

### pathA, pathB, pathC, symlinkPath, entryPoint

These sub-directories contain minimal implementations of two
`PythonPluginSystemPlugin`s:

- `PackagePlugin` : A plugin implemented in a python package.
- `ModulePlugin` A plugin implemented in a single-file python module.

`PackagePlugin` is available via `pathB`, and
`entryPoint/site-packages`. `ModulePlugin` is installed in `pathA`
and `pathC`.

`symlinkPath` exposes `pathA` and `pathB` plugins via symlinks.

These permutations allow path precedence and traversal behaviors
to be properly tested.

`entryPoint` also provides an `openassetio.manager_plugin` entry point
that allows it to be used with `dist-info` based discovery.

### broken

This directory provides broken plugins. Either missing a `plugin`
variable, or raising an exception during import.

## Use in tests

All plugins can be loaded using the standard `$OPENASSETIO_PLUGIN_PATH`
path-based discovery mechanism - by adding their parent directory e.g:

```python
monkeypatch.setenv("OPENASSETIO_PLUGIN_PATH", "/path/to/pathC")
```

`entryPoint` and `broken` plugins also expose an entry point, and so can
be used via the alternate `dist-info` based approach, e.g:

```python
monkeypatch.syspath_prepend("/path/to/dir/broken/site-packages")
```

## Updating entry point plugins

Update the package code in the respective `src`, then, from its parent
directory:

```bash
python -m pip install ./src -t ./site-packages
```

Each `dist-info` dir will contain an additional `direct_url.json` file
(which is mandated for path-based/local installs). This is not required,
for our uses and leaks information about your local dev environment so
should be removed, along with its corresponding entry in `RECORD`.

Any additional references to build `pyc`s should be removed too.

You can now commit these changes (both to `src` and `site-packages` as
normal.
