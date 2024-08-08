# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Foundry Visionmongers Ltd
#
# A Docker container for building OpenAssetIO
# Is an extension of the ASWF 2024 image, with additional OpenAssetIO
# dependencies added in.
#

FROM aswf/ci-base:2024.1 AS openassetio-dependencies
# Build dependencies
# Pull and install toml++
RUN git clone --branch v3.2.0 https://github.com/marzer/tomlplusplus
RUN cd tomlplusplus && cmake -S . -B build && cmake --build build && cmake --install build

# Pull and install trompeloeil
RUN git clone --branch v42 https://github.com/rollbear/trompeloeil
RUN cd trompeloeil && cmake -S . -B build && cmake --build build && cmake --install build

# Pull and install fmt
RUN git clone --branch 9.1.0 https://github.com/fmtlib/fmt
RUN cd fmt && cmake -S . -B build -DFMT_MASTER_PROJECT=OFF -DFMT_INSTALL=ON && \
     cmake --build build --parallel && cmake --install build

# Pull and install ada
RUN git clone --branch v2.7.4 https://github.com/ada-url/ada
RUN cd ada && cmake -S . -B build -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DADA_TESTING=OFF && \
     cmake --build build --parallel && cmake --install build

# Pull and install pcre2
RUN git clone --branch pcre2-10.42 https://github.com/PCRE2Project/pcre2
RUN cd pcre2 && cmake -S . -B build \
    -DPCRE2_STATIC_PIC=ON -DPCRE2_SUPPORT_JIT=ON -DPCRE2_BUILD_PCRE2GREP=OFF \
    -DPCRE2_BUILD_TESTS=OFF && \
     cmake --build build --parallel && cmake --install build

# Test dependencies
# Pull and install catch2
RUN git clone --branch v2.13.10 https://github.com/catchorg/Catch2
RUN cd Catch2 && cmake -S . -B build -DCATCH_BUILD_TESTING=OFF && cmake --build build && cmake --install build

FROM aswf/ci-base:2024.1
# Copy toml++
COPY --from=openassetio-dependencies /usr/local/include/toml++ /usr/local/include/toml++
COPY --from=openassetio-dependencies /usr/local/share/tomlplusplus /usr/local/share/tomlplusplus
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/tomlplusplus /usr/local/lib64/cmake/tomlplusplus

# Copy catch2
COPY --from=openassetio-dependencies /usr/local/include/catch2 /usr/local/include/catch2
COPY --from=openassetio-dependencies /usr/local/share/Catch2 /usr/local/share/Catch2
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/Catch2 /usr/local/lib64/cmake/Catch2

# Copy fmt
COPY --from=openassetio-dependencies /usr/local/include/fmt /usr/local/include/fmt
COPY --from=openassetio-dependencies /usr/local/lib64/libfmt.a /usr/local/lib64/libfmt.a
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/fmt /usr/local/lib64/cmake/fmt

# Copy ada
COPY --from=openassetio-dependencies /usr/local/include/ada /usr/local/include/ada
COPY --from=openassetio-dependencies /usr/local/include/ada.h /usr/local/include/ada.h
COPY --from=openassetio-dependencies /usr/local/lib64/libada.a /usr/local/lib64/libada.a
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/ada /usr/local/lib64/cmake/ada

# Copy pcre2
COPY --from=openassetio-dependencies /usr/local/include/pcre2.h /usr/local/include/pcre2.h
COPY --from=openassetio-dependencies /usr/local/include/pcre2posix.h /usr/local/include/pcre2posix.h
COPY --from=openassetio-dependencies /usr/local/lib64/libpcre2-8.a /usr/local/lib64/libpcre2-8.a
COPY --from=openassetio-dependencies /usr/local/lib64/libpcre2-posix.a /usr/local/lib64/libpcre2-posix.a
COPY --from=openassetio-dependencies /usr/local/cmake/pcre2-config.cmake /usr/local/cmake/pcre2-config.cmake
COPY --from=openassetio-dependencies /usr/local/cmake/pcre2-config-version.cmake /usr/local/cmake/pcre2-config-version.cmake
# Copy trompeloeil
# Trompeloeil installs itself into relevent test framework folders, so
# some relevent parts of it for us is copied over with include/catch2
# above.
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/trompeloeil /usr/local/lib64/cmake/trompeloeil
COPY --from=openassetio-dependencies /usr/local/include/trompeloeil.hpp /usr/local/include/trompeloeil.hpp

# libabigail providing abidiff tool for ABI checking
RUN yum install -y libabigail-2.5-1.el8

# * Update CMake. See cmake_minimum_required in top-level CMakeLists.txt.
# * Add pybind11-stubgen for generating .pyi stub files
RUN pip install cmake==3.28.3 pybind11-stubgen==2.5.1

LABEL org.opencontainers.image.name="openassetio-build"
LABEL org.opencontainers.image.title="OpenAssetIO VFX CY2024 Build Docker Image"
LABEL org.opencontainers.image.description="Extends ASWF CY2024, adds OpenAssetIO dependencies"
LABEL org.opencontainers.image.url="https://github.com/OpenAssetIO/"
LABEL org.opencontainers.image.source="https://github.com/OpenAssetIO/OpenAssetIO/tree/main/resources/build/Dockerfile"
LABEL org.opencontainers.image.vendor="OpenAssetIO"

# CY23+ images are based on nvidia/cuda, which prints a banner to stdout
# before handing off to the given command. This is annoying, especially
# when we want to process the stdout of some command (e.g. `abidw`). So
# override to remove the entrypoint.
ENTRYPOINT []
