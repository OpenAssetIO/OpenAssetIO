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
        # TODO(DF): fmt v10 forcibly exports the symbol for its
        #  `format_error` exception in GCC, making it not a true private
        #  dependency. So pin to v9 for now.
        self.requires("fmt/9.1.0")

    def configure(self):
        self.options["fmt"].header_only = True
        self.options["ada"].shared = False

        self.options["pcre2"].shared = False
        # Unnecessary - we only do UTF-8
        self.options["pcre2"].build_pcre2_16 = False
        self.options["pcre2"].build_pcre2_32 = False
        # Unnecessary - we don't need the command-line tool.
        self.options["pcre2"].build_pcre2grep = False
        # Enable optimising patterns with additional compile step.
        self.options["pcre2"].support_jit = True

