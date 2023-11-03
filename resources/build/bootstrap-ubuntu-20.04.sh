#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail
sudo apt-get update
# Install gcc, linters, build tools used by conan and Python 3.
sudo apt-get install -y build-essential pkgconf clang-format-12 clang-tidy-12 python3-pip ccache

# Install additional build tools.
sudo pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
export CONAN_HOME="$HOME/conan"
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install \
 --output-folder "$WORKSPACE/.conan" \
 --profile:host resources/build/vfx22.profile \
 --profile:build resources/build/vfx22.profile \
 "$WORKSPACE/resources/build"
# Ensure we have the expected version of clang-* available
sudo update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-12 10
sudo update-alternatives --install /usr/bin/clang-format clang-format /usr/bin/clang-format-12 10
sudo update-alternatives --set clang-tidy /usr/bin/clang-tidy-12
sudo update-alternatives --set clang-format /usr/bin/clang-format-12
