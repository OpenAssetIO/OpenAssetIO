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
These tests check the functionality of the PythonPluginSystem class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os

import pytest

from openassetio.log import ConsoleLogger
from openassetio.pluginSystem import PythonPluginSystem


class Test_PythonPluginSystem_scan:
    def test_when_path_contains_a_module_plugin_definition_then_it_is_loaded(
        self, a_plugin_system, a_module_plugin_path, module_plugin_identifier
    ):
        a_plugin_system.scan(a_module_plugin_path)
        assert a_plugin_system.identifiers() == [
            module_plugin_identifier,
        ]

    def test_when_path_contains_a_package_plugin_definition_then_it_is_loaded(
        self, a_plugin_system, a_package_plugin_path, package_plugin_identifier
    ):
        a_plugin_system.scan(a_package_plugin_path)
        assert a_plugin_system.identifiers() == [
            package_plugin_identifier,
        ]

    def test_when_path_contains_multiple_entries_then_all_plugins_are_loaded(
        self,
        a_plugin_system,
        a_package_plugin_path,
        a_module_plugin_path,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        combined_path = os.pathsep.join([a_package_plugin_path, a_module_plugin_path])
        a_plugin_system.scan(combined_path)

        expected_identifiers = set([package_plugin_identifier, module_plugin_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_multiple_plugins_share_identifiers_then_leftmost_is_used(
        self, a_plugin_system, the_resources_directory_path, module_plugin_identifier
    ):
        # The module plugin exists in pathA and pathC
        path_a = os.path.join(the_resources_directory_path, "pathA")
        path_c = os.path.join(the_resources_directory_path, "pathC")

        a_plugin_system.scan(paths=os.pathsep.join((path_a, path_c)))
        assert "pathA" in a_plugin_system.plugin(module_plugin_identifier).__file__

        a_plugin_system.reset()

        a_plugin_system.scan(paths=os.pathsep.join((path_c, path_a)))
        assert "pathC" in a_plugin_system.plugin(module_plugin_identifier).__file__

    def test_when_path_contains_symlinks_then_plugins_are_loaded(
        self,
        a_plugin_system,
        a_plugin_path_with_symlinks,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        a_plugin_system.scan(a_plugin_path_with_symlinks)

        expected_identifiers = set([package_plugin_identifier, module_plugin_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_scan_called_multiple_times_then_plugins_combined(
        self,
        a_plugin_system,
        a_package_plugin_path,
        a_module_plugin_path,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        a_plugin_system.scan(paths=a_package_plugin_path)
        a_plugin_system.scan(paths=a_module_plugin_path)

        expected_identifiers = set([package_plugin_identifier, module_plugin_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers


@pytest.fixture
def a_plugin_system(a_logger):
    return PythonPluginSystem(a_logger)


# We use a real logger vs a mock, as it makes debugging test failures
# easier as it surfaces any actual in-flight errors from the plugin
# system.
@pytest.fixture
def a_logger():
    return ConsoleLogger()
