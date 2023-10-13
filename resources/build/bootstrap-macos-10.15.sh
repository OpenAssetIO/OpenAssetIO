#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
export CONAN_HOME="$HOME/conan"
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install \
 --output-folder "$WORKSPACE/.conan" \
 --profile:host resources/build/vfx22.profile \
 --profile:build resources/build/vfx22.profile \
 "$WORKSPACE/resources/build"
