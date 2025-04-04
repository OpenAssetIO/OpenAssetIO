#
#   Copyright 2013-2025 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Helper fixtures for testing the Python plugin system
"""
# pylint: disable=missing-function-docstring,redefined-outer-name
# pylint: disable=invalid-name

import os

import pytest


@pytest.fixture
def the_manager_plugin_module_hook():
    return "openassetioPlugin"


@pytest.fixture
def plugin_b_identifier():
    return "org.openassetio.test.pluginSystem.resources.pluginB"


@pytest.fixture
def deprecated_plugin_identifier():
    return "org.openassetio.test.pluginSystem.resources.deprecated"


@pytest.fixture
def entry_point_plugin_identifier(plugin_b_identifier):
    return plugin_b_identifier


@pytest.fixture
def a_python_plugin_path_with_symlinks(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "symlinkPath")


@pytest.fixture
def a_cpp_plugin_path_with_symlinks(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "symlinkPath")


@pytest.fixture
def a_symlink_to_a_cpp_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "pathASymlink")


@pytest.fixture
def a_python_module_plugin_path(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "pathA")


@pytest.fixture
def a_cpp_manager_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "managerA")


@pytest.fixture
def a_python_package_plugin_path(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "pathB")


@pytest.fixture
def a_deprecated_plugin_path(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "deprecated")


@pytest.fixture
def broken_python_plugins_path(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "broken", "site-packages")


@pytest.fixture
def broken_cpp_plugins_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "broken")


@pytest.fixture
def an_entry_point_package_plugin_root(the_python_resources_directory_path):
    return os.path.join(the_python_resources_directory_path, "entryPoint", "site-packages")


@pytest.fixture
def the_python_resources_directory_path():
    return os.path.join(os.path.dirname(__file__), "resources")
