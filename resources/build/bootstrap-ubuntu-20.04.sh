#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail
sudo apt-get update
# Install gcc and Python 3 (via pip, which will bring along Python 3 as
# a dependency).
sudo apt-get install -y build-essential python3-pip
# Install system packages required for the Python 3.9 conan package.
# These would be installed as part of the conan package install, but
# we're caching the conan directory via the `actions/cache` Github
# action, so a fresh Github VM is left without these system packages.
sudo apt-get install -y  --no-install-recommends libfontenc-dev libx11-xcb-dev libxaw7-dev \
    libxcb-dri3-dev libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1-dev libxcb-randr0-dev \
    libxcb-render-util0-dev libxcb-shape0-dev libxcb-sync-dev libxcb-util-dev libxcb-xfixes0-dev \
    libxcb-xinerama0-dev libxcb-xkb-dev libxcomposite-dev libxcursor-dev libxdamage-dev \
    libxfixes-dev libxi-dev libxinerama-dev libxmu-dev libxmuu-dev libxpm-dev libxrandr-dev \
    libxres-dev libxss-dev libxtst-dev libxv-dev libxvmc-dev libxxf86vm-dev

# Install additional build tools.
sudo pip3 install conan==1.45.0 cmake==3.21 ninja==1.10.2.3
# Use explicit predictable conan root path, to be used for both packages
# and conan CMake toolchain config.
export CONAN_USER_HOME="$HOME/conan"
# Use old C++11 ABI as per VFX Reference Platform CY2022.
conan config set compiler.libcxx=libstdc++
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder "$CONAN_USER_HOME" --build=missing \
    "$GITHUB_WORKSPACE/resources/build"
