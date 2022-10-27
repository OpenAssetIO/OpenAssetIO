#!/usr/bin/env bash
# This bootstrap script is used by both the Github CI action and the
# Vagrant VM configuration.

set -xeo pipefail
sudo apt-get update
# Install gcc, linters, build tools used by conan and Python 3.
sudo apt-get install -y build-essential pkgconf clang-format-12 clang-tidy-12 python3-pip ccache

# Install system packages required for the Python 3.9 conan package.
# These would be installed as part of the conan package install, but
# we're caching the conan directory via the `actions/cache` Github
# action, so a fresh Github VM is left without these system packages.
sudo apt-get install -y --no-install-recommends libfontenc-dev libice-dev libsm-dev libx11-dev \
 libx11-xcb-dev libxau-dev libxaw7-dev libxcb-dri3-dev libxcb-icccm4-dev libxcb-image0-dev \
 libxcb-keysyms1-dev libxcb-randr0-dev libxcb-render0-dev libxcb-render-util0-dev \
 libxcb-shape0-dev libxcb-sync-dev libxcb-util-dev libxcb-xfixes0-dev libxcb-xinerama0-dev \
 libxcb-xkb-dev libxcomposite-dev libxcursor-dev libxdamage-dev libxdmcp-dev libxext-dev \
 libxfixes-dev libxi-dev libxinerama-dev libxkbfile-dev libxmu-dev libxmuu-dev libxpm-dev \
 libxrandr-dev libxrender-dev libxres-dev libxss-dev libxt-dev libxtst-dev libxv-dev libxvmc-dev \
 libxxf86vm-dev uuid-dev xkb-data xtrans-dev

# Install additional build tools.
sudo pip3 install -r "$WORKSPACE/resources/build/requirements.txt"
# Use explicit predictable conan root path, where packages are cached.
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
# TODO(DF): conan<1.51 (not yet released) has a bug that means we have
# to allow conan recipes to try to install system packages, even if the
# system packages are already available. In particular, this affects
# recent versions of the xorg/system recipe (a dependency of cpython).
# The problem is reported and fixed in https://github.com/conan-io/conan/pull/11712
conan install --install-folder "$WORKSPACE/.conan" --build=missing \
    -c tools.system.package_manager:mode=install \
    -c tools.system.package_manager:sudo=True \
    "$WORKSPACE/resources/build"
# Ensure we have the expected version of clang-* available
sudo update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-12 10
sudo update-alternatives --install /usr/bin/clang-format clang-format /usr/bin/clang-format-12 10
sudo update-alternatives --set clang-tidy /usr/bin/clang-tidy-12
sudo update-alternatives --set clang-format /usr/bin/clang-format-12
