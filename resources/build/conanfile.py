from conans import ConanFile, tools
from conan.tools.cmake import CMakeDeps, CMakeToolchain


class OpenAssetIOConan(ConanFile):
    settings = "os", "build_type"
    # Generate a CMake toolchain preamble file `conan_paths.cmake`,
    # which augments package search paths with conan package
    # directories.
    # TODO(DF): This is deprecated and should be swapped for the
    # CMakeToolchain generator, but that is not yet compatible with the
    # cpython recipe (it does not specify `builddirs` so is not added to
    # the CMAKE_PREFIX_PATH).
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
        if not tools.get_env("OPENASSETIO_CONAN_SKIP_CPYTHON", False):
            self.requires("cpython/3.9.7")
        # Same as ASWF CY2022 Docker image:
        # https://github.com/AcademySoftwareFoundation/aswf-docker/blob/master/ci-base/README.md
        self.requires("pybind11/2.8.1")

    def build_requirements(self):
        # TOML library
        self.tool_requires("tomlplusplus/3.2.0")
        # Test framework
        self.tool_requires("catch2/2.13.8")
        # Mocking library
        self.tool_requires("trompeloeil/42")

    def configure(self):
        if self.settings.os == "Windows":
            # Without the following, ConanCenter's `cpython` package
            # doesn't get installed with all artifacts on Windows, e.g.
            # `python -m venv` doesn't work. See:
            # https://github.com/conan-io/conan-center-index/issues/9333
            # However, with the following, the package's bundled Python
            # interpreter doesn't work on Linux because it cannot find
            # libpython (RPATH issue). So we must make this conditional
            # on the OS.
            self.options["cpython"].shared = True
