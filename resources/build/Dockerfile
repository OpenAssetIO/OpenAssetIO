# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The Foundry Visionmongers Ltd
#
# A Docker container for building OpenAssetIO
# Is an extension of the ASWF 2022 image, with additional OpenAssetIO
# dependencies added in.
#

FROM aswf/ci-base:2022.2 AS openassetio-dependencies
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

# Test dependencies
# Pull and install catch2
RUN git clone --branch v2.13.10 https://github.com/catchorg/Catch2
RUN cd Catch2 && cmake -S . -B build -DCATCH_BUILD_TESTING=OFF && cmake --build build && cmake --install build

FROM aswf/ci-base:2022.2
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

# Copy trompeloeil
# Trompeloeil installs itself into relevent test framework folders, so
# some relevent parts of it for us is copied over with include/catch2
# above.
COPY --from=openassetio-dependencies /usr/local/lib64/cmake/trompeloeil /usr/local/lib64/cmake/trompeloeil
COPY --from=openassetio-dependencies /usr/local/include/trompeloeil.hpp /usr/local/include/trompeloeil.hpp

LABEL org.opencontainers.image.name="openassetio-build"
LABEL org.opencontainers.image.title="OpenAssetIO VFX CY2022 Build Docker Image"
LABEL org.opencontainers.image.description="Extends ASWF CY2022, adds OpenAssetIO dependencies"
LABEL org.opencontainers.image.url="https://github.com/OpenAssetIO/"
LABEL org.opencontainers.image.source="https://github.com/OpenAssetIO/OpenAssetIO/tree/main/resources/build/Dockerfile"
LABEL org.opencontainers.image.vendor="OpenAssetIO"
