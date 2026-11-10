#!/usr/bin/env bash
# This bootstrap script is used by the Github CI action.

set -xeo pipefail

# Conan Center only has pre-built binaries for a limited set of clang
# versions. Install the tools required to build packages locally.
brew install automake autoconf

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
