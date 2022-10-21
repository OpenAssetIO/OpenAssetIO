#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
export CONAN_USER_HOME="$HOME/conan"
# Create default conan profile so we can configure it before install.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force

# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder "$WORKSPACE/.conan" --build=missing \
    "$WORKSPACE/resources/build"
