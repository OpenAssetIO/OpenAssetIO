#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
def module_plugin_identifier():
    return "org.openassetio.test.pluginSystem.resources.modulePlugin"


@pytest.fixture
def package_plugin_identifier():
    return "org.openassetio.test.pluginSystem.resources.packagePlugin"


@pytest.fixture
def a_plugin_path_with_symlinks(the_resources_directory_path):
    return os.path.join(the_resources_directory_path, "symlinkPath")


@pytest.fixture
def a_module_plugin_path(the_resources_directory_path):
    return os.path.join(the_resources_directory_path, "pathA")


@pytest.fixture
def a_package_plugin_path(the_resources_directory_path):
    return os.path.join(the_resources_directory_path, "pathB")


@pytest.fixture
def the_resources_directory_path():
    return os.path.join(os.path.dirname(__file__), "resources")
