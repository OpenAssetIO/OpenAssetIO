# Metadata files to be bundled with the installed package

This directory contains files used for package discovery in the install
tree.

The CMake config files are used to allow CMake's `find_package` to
discover an installed OpenAssetIO CMake package (see [CMake docs](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html)
for more info).

Some of the config files are templates (as evidenced by the `.in`
suffix), and will be rendered to their final form as part of a CMake
build/install.
