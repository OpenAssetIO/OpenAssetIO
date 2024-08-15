#!/usr/bin/env bash

set -xeo pipefail

# This script not runnable from outside a cibuildwheel environment.
if [ "$CIBUILDWHEEL" != "1" ]
then
  echo "Error. Attempting to run cibuildwheel-manylinux bootstrap outside of cibuildwheel"
  exit 1
fi

# Install additional build tools.
pip3 install -r "resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
export CONAN_USER_HOME="$HOME/conan"

# Create default conan profile so we can configure it before install.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force
# Use new/non-deprecated C++11 ABI to match VFX Reference Platform
# CY23+.
conan profile update settings.compiler.libcxx=libstdc++11 default
# If we need to pin a package to a specific Conan recipe revision, then
# we need to explicitly opt-in to this functionality.
conan config set general.revisions_enabled=True
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder ".conan" --build=missing \
    "resources/build"
