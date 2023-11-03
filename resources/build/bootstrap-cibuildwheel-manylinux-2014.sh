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
export CONAN_HOME="$HOME/conan"

# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install \
 --output-folder .conan \
 --profile:host resources/build/vfx22.profile \
 --profile:build resources/build/vfx22.profile \
 resources/build
