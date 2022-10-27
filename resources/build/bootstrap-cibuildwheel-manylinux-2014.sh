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

# Create default conan profile so we can configure it before instlibXcomposite-develall.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force
# Use old C++11 ABI as per VFX Reference Platform CY2022. Not strictly
# necessary as this is the default for conan, but we can't be certain
# it'll remain the default in future.
conan profile update settings.compiler.libcxx=libstdc++ default

# Install openassetio third-party dependencies from public Conan Center
# package repo.
export OPENASSETIO_CONAN_SKIP_CPYTHON="True"
conan install --install-folder ".conan" --build=missing \
    "resources/build"