{#- SPDX-License-Identifier: Apache-2.0 -#}
{#- Copyright 2026 The Foundry Visionmongers Ltd -#}
{%- set os = detect_api.detect_os() %}
{%- set compiler, version, compiler_exe = detect_api.detect_default_compiler() %}
# Best-effort alignment with VFX Reference Platform CY2024
# (https://vfxplatform.com). Everything else is auto-detected.

[settings]
build_type = Release
os = {{ os }}
arch = {{ detect_api.detect_arch() }}
compiler = {{ compiler }}
compiler.cppstd = 17
compiler.version = {{ detect_api.default_compiler_version(compiler, version) }}
{%- if os == "Linux" %}
# New (non-deprecated) C++11 libstdc++ ABI.
compiler.libcxx = libstdc++11
{%- elif compiler != "msvc" %}
compiler.libcxx = {{ detect_api.detect_libcxx(compiler, version, compiler_exe) }}
{%- endif %}
{%- if compiler == "msvc" %}
# Deliberately /MD, to match the Release-built dependencies and CPython.
# Debug consumer builds also get /MD, since the runtime type is derived
# from this profile's Release build_type, before `&:build_type` applies.
compiler.runtime = dynamic
{%- endif %}
{%- if os == "Macos" %}
# Deployment target, matching CMAKE_OSX_DEPLOYMENT_TARGET.
os.version = 11.0
{%- endif %}

[conf]
# Without this, Conan defaults to the Visual Studio generator on MSVC,
# and the toolchain then force-sets CMAKE_GENERATOR_PLATFORM and
# CMAKE_GENERATOR_TOOLSET, which breaks configuring with `-G Ninja`.
tools.cmake.cmaketoolchain:generator = Ninja

[options]
fmt/*:header_only=True
ada/*:shared=False
pcre2/*:shared=False
# Unnecessary - we only do UTF-8
pcre2/*:build_pcre2_16=False
pcre2/*:build_pcre2_32=False
# Unnecessary - we don't need the command-line tool.
pcre2/*:build_pcre2grep=False
# Enable optimising patterns with additional compile step.
pcre2/*:support_jit=True
