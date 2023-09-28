# Metadata files to be bundled with the installed package

This directory contains files used for package discovery in the install
tree.

This includes the CMake config files, as well as a Python "dist-info"
bundle.

The CMake config files are used to allow CMake's `find_package` to
discover an installed OpenAssetIO CMake package (see [CMake docs](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html)
for more info).

The Python dist-info allows Python package managers (such as pip) to
detect the presence of an `openassetio` package, and is configured such
that a well-behaved package manager will error when trying to overwrite
it. Specifically, the dist-info deliberately excludes a `RECORD` file
(see [Python docs](https://packaging.python.org/en/latest/specifications/recording-installed-packages/#intentionally-preventing-changes-to-installed-packages)
for more info).

Some of the config files are templates (as evidenced by the `.in`
suffix), and will be rendered to their final form as part of a CMake
build/install.
