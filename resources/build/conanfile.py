# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 The Foundry Visionmongers Ltd
"""
Conan consumer recipe for OpenAssetIO's third-party dependencies.
"""

from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain


class OpenAssetIOConan(ConanFile):
    """
    Declares the dependencies required to build and test OpenAssetIO.
    """

    settings = "os", "arch", "compiler", "build_type"

    default_options = {
        "fmt/*:header_only": True,
        "ada/*:shared": False,
        "pcre2/*:shared": False,
        # Unnecessary - we only do UTF-8
        "pcre2/*:build_pcre2_16": False,
        "pcre2/*:build_pcre2_32": False,
        # Unnecessary - we don't need the command-line tool.
        "pcre2/*:build_pcre2grep": False,
        # Enable optimising patterns with additional compile step.
        "pcre2/*:support_jit": True,
    }

    def requirements(self):
        """
        Declare third-party dependencies.
        """
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

    def generate(self):
        """
        Generate CMake config files and the CMake toolchain file.
        """
        CMakeDeps(self).generate()
        toolchain = CMakeToolchain(self)
        # The `output_dirs` block sets plain CMAKE_INSTALL_BINDIR et al.
        # variables, which would shadow the project's presets and any
        # user-supplied values.
        toolchain.blocks.remove("output_dirs")
        toolchain.generate()
