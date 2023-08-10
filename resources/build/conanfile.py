from conans import ConanFile, tools
from conan.tools.cmake import CMakeDeps


class OpenAssetIOConan(ConanFile):
    settings = "os", "build_type"
    # Generate a CMake toolchain preamble file `conan_paths.cmake`,
    # which augments package search paths with conan package
    # directories.
    # TODO(DF): This is deprecated and should be swapped for the
    # CMakeToolchain generator.
    generators = "cmake_paths"

    def generate(self):
        """
        This function is called at the end of a `conan install` and is
        responsible for generating build toolchain helpers.
        """
        # Generate `<PackageName>Config.cmake` files for each
        # dependency, which CMake's `find_package` will locate and
        # parse.
        # Note: we override the configuration and re-run multiple times
        # to allow us to use a different configuration for dependencies
        # than we use for the main project. See
        # https://github.com/conan-io/conan/issues/11607#issuecomment-1188500937
        deps = CMakeDeps(self)
        deps.configuration = "Release"
        deps.generate()
        deps.configuration = "Debug"
        deps.generate()
        deps.configuration = "RelWithDebInfo"
        deps.generate()

    def requirements(self):
        # CY2022
        self.requires("pybind11/2.10.1")
        # TOML library
        self.requires("tomlplusplus/3.2.0")
        # Test framework
        self.requires("catch2/2.13.8")
        # Mocking library
        self.requires("trompeloeil/42")
