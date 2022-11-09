# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The Foundry Visionmongers Ltd
#
# A Docker container for building OpenAssetIO
# Is an extension of the ASWF 2022 image, with additional OpenAssetIO
# dependencies added in.
#

FROM aswf/ci-base:2022.2 AS tomlplusplus-build
# Pull and install toml++
RUN git clone --branch v3.2.0 https://github.com/marzer/tomlplusplus
RUN cd tomlplusplus && cmake -S . -B build && cmake --build build && cmake --install build

FROM aswf/ci-base:2022.2
COPY --from=tomlplusplus-build /usr/local/include/toml++ /usr/local/include/toml++
COPY --from=tomlplusplus-build /usr/local/share/tomlplusplus /usr/local/share/tomlplusplus
COPY --from=tomlplusplus-build /usr/local/lib64/cmake/tomlplusplus /usr/local/lib64/cmake/tomlplusplus

LABEL org.opencontainers.image.name="openassetio-build"
LABEL org.opencontainers.image.title="OpenAssetIO VFX CY2022 Build Docker Image"
LABEL org.opencontainers.image.description="Extends ASWF CY2022, adds OpenAssetIO dependencies"
LABEL org.opencontainers.image.url="https://github.com/OpenAssetIO/"
LABEL org.opencontainers.image.source="https://github.com/OpenAssetIO/OpenAssetIO/tree/main/resources/build/Dockerfile"
LABEL org.opencontainers.image.vendor="OpenAssetIO"
