#!/usr/bin/env bash
# This bootstrap script is used by the Github CI action.

set -xeo pipefail
sudo apt-get update
# Install gcc, linters, build tools used by conan and Python 3.
sudo apt-get install -y build-essential pkgconf python3-pip ccache

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
