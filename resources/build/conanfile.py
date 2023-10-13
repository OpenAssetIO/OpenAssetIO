# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The Foundry Visionmongers Ltd
"""
Conan consumer recipe for OpenAssetIO's third-party dependencies.
"""

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeDeps, CMakeToolchain


class OpenAssetIOConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        # Python bindings
        # Note: pybind11 is not a private dependency and can conflict
        # with other versions in the same application. See
        # https://github.com/pybind/pybind11/issues/5359
        self.requires("pybind11/2.9.2")
        # TOML library
        self.requires("tomlplusplus/3.2.0")
        # URL processing
        self.requires("ada/2.7.4")
        # Regex
        self.requires("pcre2/10.42")
        # Test framework
        self.requires("catch2/2.13.8")
        # Mocking library
        self.requires("trompeloeil/42")
        self.requires("fmt/9.1.0")

    def validate(self):
        # `Regex` unconditionally JIT-compiles patterns, but ConanCenter's
        # pcre2 recipe defaults `support_jit` to off.
        if not self.dependencies["pcre2"].options.support_jit:
            raise ConanInvalidConfiguration(
                'pcre2 must be built with JIT support: i.e. "pcre2/*:support_jit=True".'
            )

    def generate(self):
        CMakeDeps(self).generate()
        toolchain = CMakeToolchain(self)
        # The `output_dirs` block sets plain CMAKE_INSTALL_BINDIR et al.
        # variables, which would shadow the project's presets and any
        # user-supplied values.
        toolchain.blocks.remove("output_dirs")
        toolchain.generate()
