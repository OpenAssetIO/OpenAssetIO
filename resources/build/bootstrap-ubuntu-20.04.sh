#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail
sudo apt-get update
# Install gcc, linters, build tools used by conan and Python 3.
sudo apt-get install -y build-essential pkgconf clang-format-12 clang-tidy-12 python3-pip ccache

# Install additional build tools.
pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
export CONAN_USER_HOME="$HOME/conan"
# Create default conan profile so we can configure it before install.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force
# Use new/non-deprecated C++11 ABI to match GitHub runner's default.
# This does not match VFX Reference Platform CY22, which is currently
# our default target, but official CY22 support (including CI testing)
# is due to be removed soon.
conan profile update settings.compiler.libcxx=libstdc++11 default
# If we need to pin a package to a specific Conan recipe revision, then
# we need to explicitly opt-in to this functionality.
conan config set general.revisions_enabled=True

# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder "$WORKSPACE/.conan" --build=missing "$WORKSPACE/resources/build"
# Ensure we have the expected version of clang-* available
sudo update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-12 10
sudo update-alternatives --install /usr/bin/clang-format clang-format /usr/bin/clang-format-12 10
sudo update-alternatives --set clang-tidy /usr/bin/clang-tidy-12
sudo update-alternatives --set clang-format /usr/bin/clang-format-12
