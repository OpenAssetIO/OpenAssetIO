#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action.

set -xeo pipefail

# macOS 12 runners ship with clang 14. Conan Center only has pre-built
# binaries for clang 12. This allows packages to be built locally.
brew install automake autoconf

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
