#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail
sudo apt-get update
# Install gcc, clang-tidy and Python 3.
sudo apt-get install -y build-essential clang-tidy-12 python3-pip
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
sudo pip3 install conan==1.45.0 cmake==3.21 ninja==1.10.2.3 cpplint==1.5.5
# Use explicit predictable conan root path, to be used for both packages
# and conan CMake toolchain config.
export CONAN_USER_HOME="$HOME/conan"
# Create default conan profile so we can configure it before install.
# Use --force so that if it already exists we don't error out.
conan profile new default --detect --force
# Use old C++11 ABI as per VFX Reference Platform CY2022. Not strictly
# necessary as this is the default for conan, but we can't be certain
# it'll remain the default in future.
conan profile update settings.compiler.libcxx=libstdc++ default
# Install openassetio third-party dependencies from public Conan Center
# package repo.
conan install --install-folder "$CONAN_USER_HOME" --build=missing \
    "$GITHUB_WORKSPACE/resources/build"
