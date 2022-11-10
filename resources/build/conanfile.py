from conans import ConanFile, CMake, tools


class OpenAssetIOConan(ConanFile):
    generators = (
        # Generate a CMake toolchain preamble file `conan_paths.cmake`,
        # which augments package search paths with conan package
        # directories.
        "cmake_paths",
        # Generate `Find<PackageName>.cmake` finders, required for
        # various public ConanCenter packages (e.g. pybind11) since they
        # disallow bundling of `<PackageName>Config.cmake`-like files in
        # the package.
        "cmake_find_package",
    )
    settings = "os"

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
