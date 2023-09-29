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

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import sys
from typing import List

import pytest

from openassetio import errors
from openassetio.log import ConsoleLogger
from openassetio.pluginSystem import PythonPluginSystem


# We use this entry point to allow us to share test resources with
# the implementation factory tests.
PLUGIN_ENTRY_POINT_GROUP = "openassetio.manager_plugin"


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

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, broken_plugins_path, mock_logger
    ):
        plugin_system = PythonPluginSystem(mock_logger)
        plugin_system.scan(broken_plugins_path)

        assert not plugin_system.identifiers()
        missing_plugin_path = os.path.join(broken_plugins_path, "missing_plugin.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            f"PythonPluginSystem: No top-level 'plugin' variable {missing_plugin_path}",
        )
        raises_exception_path = os.path.join(broken_plugins_path, "raises_exception.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            StringContaining(
                [
                    f"PythonPluginSystem: Caught exception loading {raises_exception_path}:\n",
                    f'  File "{raises_exception_path}", line 4, in <module>\n',
                    '    raise RuntimeError("An exception")',
                ]
            ),
        )


class Test_PythonPluginSystem_scan_entry_points:
    def test_when_no_package_with_entry_point_installed_then_nothing_loaded_and_true_returned(
        self, a_plugin_system
    ):
        assert a_plugin_system.scan_entry_points(PLUGIN_ENTRY_POINT_GROUP) is True
        assert not a_plugin_system.identifiers()

    def test_when_entry_point_package_installed_then_loaded_and_true_returned(
        self,
        a_plugin_system,
        an_entry_point_package_plugin_root,
        entry_point_plugin_identifier,
        monkeypatch,
    ):
        path_with_plugin = [an_entry_point_package_plugin_root] + sys.path
        monkeypatch.setattr(sys, "path", path_with_plugin)

        assert a_plugin_system.scan_entry_points(PLUGIN_ENTRY_POINT_GROUP) is True
        assert a_plugin_system.identifiers() == [entry_point_plugin_identifier]

    def test_when_importlib_metadata_missing_then_a_warning_is_loggeed_and_false_returned(
        self, mock_logger, monkeypatch
    ):
        # Remove any previously imported versions
        sys.modules.pop("importlib_metadata", None)
        monkeypatch.setattr(sys, "path", [])

        plugin_system = PythonPluginSystem(mock_logger)
        assert plugin_system.scan_entry_points("some.entrypoint") is False

        mock_logger.mock.log.assert_called_once_with(
            mock_logger.Severity.kWarning,
            "PythonPluginSystem: Can not load entry point plugins as the importlib_metadata "
            "package is unavailable.",
        )

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, broken_plugins_path, mock_logger, monkeypatch
    ):
        path_with_plugin = [broken_plugins_path] + sys.path
        monkeypatch.setattr(sys, "path", path_with_plugin)

        plugin_system = PythonPluginSystem(mock_logger)
        plugin_system.scan_entry_points(PLUGIN_ENTRY_POINT_GROUP)

        assert not plugin_system.identifiers()
        # mock_logger.mock.log.assert_called_once()
        missing_plugin_path = os.path.join(broken_plugins_path, "missing_plugin.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            f"PythonPluginSystem: No top-level 'plugin' variable {missing_plugin_path}",
        )
        raises_exception_path = os.path.join(broken_plugins_path, "raises_exception.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            StringContaining(
                [
                    "PythonPluginSystem: Caught exception loading raies_exception:\n",
                    f'  File "{raises_exception_path}", line 4, in <module>\n',
                    '    raise RuntimeError("An exception")',
                ]
            ),
        )


class Test_PythonPluginSystem_plugin:
    def test_when_plugin_not_found_then_raises_InputValidationException(self, a_plugin_system):
        with pytest.raises(
            errors.InputValidationException,
            match="PythonPluginSystem: No plug-in registered with the identifier 'nonexistent'",
        ):
            a_plugin_system.plugin("nonexistent")


@pytest.fixture
def a_plugin_system(a_logger):
    return PythonPluginSystem(a_logger)


# We use a real logger vs a mock, as it makes debugging test failures
# easier as it surfaces any actual in-flight errors from the plugin
# system.
@pytest.fixture
def a_logger():
    return ConsoleLogger()


class StringContaining:
    """
    A helper class that aids testing runtime generated strings that may
    contain unpredictable content along with known text (e.g stack
    traces).

    It only compares True to another string that contains all of the
    supplied substrings.
    """

    def __init__(self, substrings: List[str]):
        """
        @param substrings A list of substrings that must be present
        when this object is compared to a string.
        """
        self.__substrings = substrings

    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        for substring in self.__substrings:
            if substring not in other:
                return False
        return True

    def __neq__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"StringContaining({repr(self.__substrings)})"
