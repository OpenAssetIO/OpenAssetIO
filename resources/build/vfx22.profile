{%- set os = detect_api.detect_os() %}
{%- set compiler, version = detect_api.detect_compiler() %}

[settings]
build_type = Release
os = {{ os }}
arch = {{ detect_api.detect_arch() }}
compiler = {{ compiler }}
compiler.cppstd = 17
compiler.version = {{ version }}
{%- if os == "Linux" %}
compiler.libcxx = "libstdc++"
{%- elif compiler != "msvc" %}
compiler.libcxx = {{ detect_api.detect_libcxx(compiler, version) }}
{%- endif %}

[conf]
# Required since Conan v2 sets up CMake generator-specific state, fixes
# https://github.com/conan-io/conan/issues/7908
tools.cmake.cmaketoolchain:generator = "Ninja"
