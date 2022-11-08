from conans import ConanFile, CMake, tools


class OpenAssetIOConan(ConanFile):
    generators = (
        # Generate a CMake toolchain preamble file `conan_paths.cmake`,
        # which augments package search paths with conan package
        # directories.
        "cmake_paths",
        # Generate `Find<PackageName>.cmake` finders, required for various
        # public ConanCenter packages (e.g. pybind11) since they disallow
        # bundling of `<PackageName>Config.cmake`-like files in the package.
        "cmake_find_package",
    )
    settings = "os"

    def build_requirements(self):
        # CY2022
        if not tools.get_env("OPENASSETIO_CONAN_SKIP_CPYTHON", False):
            self.tool_requires("cpython/3.9.7")
        # Later versions than ASWF CY2022 (pybind11 v2.8.1) required to
        # support more recent Python versions.
        self.tool_requires("pybind11/2.10.0")
        # Test framework
        self.tool_requires("catch2/2.13.8")
        # Mocking library
        self.tool_requires("trompeloeil/42")

    def configure(self):
        if self.settings.os == "Windows":
            # Without the following, ConanCenter's `cpython` package
            # doesn't get installed with all artifacts on Windows, e.g.
            # `python -m venv` doesn't work. See:
            # https://github.com/conan-io/conan-center-index/issues/9332
            # However, with the following, the package's bundled Python
            # interpreter doesn't work on Linux because it cannot find
            # libpython (RPATH issue). So we must make this conditional
            # on the OS.
            self.options["cpython"].shared = True
