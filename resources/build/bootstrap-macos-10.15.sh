#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail

# Install additional build tools.
pip3 install conan==1.45.0 cmake==3.21 ninja==1.10.2.3 cpplint==1.5.5
# Use explicit predictable conan root path, to be used for both packages
# and conan CMake toolchain config.
export CONAN_USER_HOME="$HOME/conan"
# Create default conan profile so we can configure it before install.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder "$CONAN_USER_HOME" --build=missing \
    "$GITHUB_WORKSPACE/resources/build"
