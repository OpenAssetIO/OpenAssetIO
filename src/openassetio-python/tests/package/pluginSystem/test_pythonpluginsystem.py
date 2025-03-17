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
These tests check the functionality of the PythonPluginSystem class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
from typing import List
from unittest import mock

import pytest

from openassetio import errors
from openassetio.log import ConsoleLogger
from openassetio.pluginSystem import PythonPluginSystem, PythonPluginSystemPlugin


# Entry point group used by the stub plugins in the `resources`
# directory.
PLUGIN_ENTRY_POINT_GROUP = "openassetio.manager_plugin"


class Test_PythonPluginSystem_scan:

    def test_when_no_paths_and_entry_point_disabled_by_arg_then_nothing_scanned_and_warning_logged(
        self,
        a_plugin_system_with_mocked_scanning,
        mock_logger,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        a_plugin_system_with_mocked_scanning.scan(
            "",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            True,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_paths.assert_not_called()
        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_not_called()

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            "PythonPluginSystem: No search paths specified and entry point plugins are disabled,"
            f" no plugins will load - check ${a_paths_env_var} is set.",
        )

    def test_when_no_paths_and_entry_point_disabled_by_env_then_nothing_scanned_and_warning_logged(
        self,
        a_plugin_system_with_mocked_scanning,
        mock_logger,
        monkeypatch,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        monkeypatch.setenv(a_disable_entry_point_env_var, "1")

        a_plugin_system_with_mocked_scanning.scan(
            "",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            None,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_paths.assert_not_called()
        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_not_called()

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            "PythonPluginSystem: No search paths specified and entry point plugins are disabled,"
            f" no plugins will load - check ${a_paths_env_var} is set.",
        )

    def test_when_paths_then_env_var_not_used(
        self,
        a_plugin_system_with_mocked_scanning,
        monkeypatch,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        monkeypatch.setenv(a_paths_env_var, "/some/other/path")

        a_plugin_system_with_mocked_scanning.scan(
            "/some/path",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            None,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_paths.assert_called_once_with(
            "/some/path", a_module_hook_name
        )

    def test_when_no_paths_then_env_var_used(
        self,
        a_plugin_system_with_mocked_scanning,
        monkeypatch,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        monkeypatch.setenv(a_paths_env_var, "/some/other/path")

        a_plugin_system_with_mocked_scanning.scan(
            "",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            None,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_paths.assert_called_once_with(
            "/some/other/path", a_module_hook_name
        )

    def test_when_entry_point_then_entry_points_scanned(
        self,
        a_plugin_system_with_mocked_scanning,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        a_plugin_system_with_mocked_scanning.scan(
            "",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            None,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_called_once_with(
            an_entry_point_group_name, a_module_hook_name
        )

    def test_when_entry_point_disabled_by_arg_then_entry_points_not_scanned(
        self,
        a_plugin_system_with_mocked_scanning,
        mock_logger,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        a_plugin_system_with_mocked_scanning.scan(
            "/some/path",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            True,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_not_called()
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            "Entry point based plugins are disabled",
        )

    def test_when_entry_point_disabled_by_env_then_entry_points_not_scanned(
        self,
        a_plugin_system_with_mocked_scanning,
        mock_logger,
        monkeypatch,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        monkeypatch.setenv(a_disable_entry_point_env_var, "1")

        a_plugin_system_with_mocked_scanning.scan(
            "/some/path",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            True,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_not_called()
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            "Entry point based plugins are disabled",
        )

    def test_when_entry_point_disabled_by_env_but_enabled_by_arg_then_entry_points_scanned(
        self,
        a_plugin_system_with_mocked_scanning,
        monkeypatch,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        monkeypatch.setenv(a_disable_entry_point_env_var, "1")

        a_plugin_system_with_mocked_scanning.scan(
            "/some/path",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            False,
            a_module_hook_name,
        )

        a_plugin_system_with_mocked_scanning.scan_entry_points.assert_called_once_with(
            an_entry_point_group_name, a_module_hook_name
        )

    def test_when_paths_and_entry_point_then_paths_scanned_first(
        self,
        a_plugin_system_with_mocked_scanning,
        a_paths_env_var,
        an_entry_point_group_name,
        a_disable_entry_point_env_var,
        a_module_hook_name,
    ):
        calls = mock.Mock()
        calls.attach_mock(a_plugin_system_with_mocked_scanning.scan_paths, "scan_paths")
        calls.attach_mock(
            a_plugin_system_with_mocked_scanning.scan_entry_points, "scan_entry_points"
        )

        a_plugin_system_with_mocked_scanning.scan(
            "/some/path",
            a_paths_env_var,
            an_entry_point_group_name,
            a_disable_entry_point_env_var,
            False,
            a_module_hook_name,
        )

        assert calls.mock_calls == [
            mock.call.scan_paths("/some/path", a_module_hook_name),
            mock.call.scan_entry_points(an_entry_point_group_name, a_module_hook_name),
        ]


class Test_PythonPluginSystem_scan_paths:
    def test_when_path_contains_a_module_plugin_definition_then_it_is_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_python_module_plugin_path,
        plugin_a_identifier,
    ):
        a_plugin_system.scan_paths(a_python_module_plugin_path, the_manager_plugin_module_hook)
        assert a_plugin_system.identifiers() == [
            plugin_a_identifier,
        ]

    def test_when_path_contains_a_package_plugin_definition_then_it_is_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_python_package_plugin_path,
        plugin_b_identifier,
    ):
        a_plugin_system.scan_paths(a_python_package_plugin_path, the_manager_plugin_module_hook)
        assert a_plugin_system.identifiers() == [
            plugin_b_identifier,
        ]

    def test_when_path_contains_multiple_entries_then_all_plugins_are_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_python_package_plugin_path,
        a_python_module_plugin_path,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        combined_path = os.pathsep.join(
            [a_python_package_plugin_path, a_python_module_plugin_path]
        )
        a_plugin_system.scan_paths(combined_path, the_manager_plugin_module_hook)

        expected_identifiers = set([plugin_b_identifier, plugin_a_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_path_contains_deprecated_plugin_hook_then_it_is_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_deprecated_plugin_path,
        deprecated_plugin_identifier,
    ):
        a_plugin_system.scan_paths(a_deprecated_plugin_path, the_manager_plugin_module_hook)
        assert a_plugin_system.identifiers() == [
            deprecated_plugin_identifier,
        ]

    def test_when_path_contains_deprecated_plugin_hook_then_deprecation_warning_is_logged(
        self, the_manager_plugin_module_hook, a_deprecated_plugin_path, mock_logger
    ):
        deprecated_plugin_path = os.path.join(a_deprecated_plugin_path, "deprecatedPlugin.py")
        plugin_system = PythonPluginSystem(mock_logger)
        plugin_system.scan_paths(a_deprecated_plugin_path, the_manager_plugin_module_hook)
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            "PythonPluginSystem: Use of top-level 'plugin' variable is deprecated, "
            f"use `openassetioPlugin` instead. {deprecated_plugin_path}",
        )

    def test_when_multiple_plugins_share_identifiers_then_leftmost_is_used(
        self,
        a_plugin_system,
        the_python_resources_directory_path,
        the_manager_plugin_module_hook,
        plugin_a_identifier,
    ):
        # The module plugin exists in pathA and pathC
        path_a = os.path.join(the_python_resources_directory_path, "pathA")
        path_c = os.path.join(the_python_resources_directory_path, "pathC")

        a_plugin_system.scan_paths(
            moduleHookName=the_manager_plugin_module_hook, paths=os.pathsep.join((path_a, path_c))
        )
        assert "pathA" in a_plugin_system.plugin(plugin_a_identifier).__file__

        a_plugin_system.reset()

        a_plugin_system.scan_paths(
            moduleHookName=the_manager_plugin_module_hook, paths=os.pathsep.join((path_c, path_a))
        )
        assert "pathC" in a_plugin_system.plugin(plugin_a_identifier).__file__

    def test_when_path_contains_symlinks_then_plugins_are_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_python_plugin_path_with_symlinks,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        a_plugin_system.scan_paths(
            a_python_plugin_path_with_symlinks, the_manager_plugin_module_hook
        )

        expected_identifiers = set([plugin_b_identifier, plugin_a_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_scan_called_multiple_times_then_plugins_combined(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_python_package_plugin_path,
        a_python_module_plugin_path,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        a_plugin_system.scan_paths(
            moduleHookName=the_manager_plugin_module_hook, paths=a_python_package_plugin_path
        )
        a_plugin_system.scan_paths(
            moduleHookName=the_manager_plugin_module_hook, paths=a_python_module_plugin_path
        )

        expected_identifiers = set([plugin_b_identifier, plugin_a_identifier])
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, the_manager_plugin_module_hook, broken_python_plugins_path, mock_logger
    ):
        plugin_system = PythonPluginSystem(mock_logger)
        plugin_system.scan_paths(broken_python_plugins_path, the_manager_plugin_module_hook)

        assert not plugin_system.identifiers()
        missing_plugin_path = os.path.join(broken_python_plugins_path, "missing_plugin.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            f"PythonPluginSystem: No top-level 'openassetioPlugin' variable {missing_plugin_path}",
        )
        raises_exception_path = os.path.join(broken_python_plugins_path, "raises_exception.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            StringContaining(
                [
                    f"PythonPluginSystem: Caught exception loading {raises_exception_path}:\n",
                    f'  File "{raises_exception_path}", line 5, in <module>\n',
                    '    raise RuntimeError("An exception")',
                ]
            ),
        )


class Test_PythonPluginSystem_scan_entry_points:
    def test_when_no_package_with_entry_point_installed_then_nothing_loaded_and_true_returned(
        self, a_plugin_system, the_manager_plugin_module_hook
    ):
        assert (
            a_plugin_system.scan_entry_points(
                PLUGIN_ENTRY_POINT_GROUP, the_manager_plugin_module_hook
            )
            is True
        )
        assert not a_plugin_system.identifiers()

    def test_when_entry_point_package_installed_then_loaded_and_true_returned(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        an_entry_point_package_plugin_root,
        entry_point_plugin_identifier,
        monkeypatch,
    ):
        monkeypatch.syspath_prepend(an_entry_point_package_plugin_root)

        assert (
            a_plugin_system.scan_entry_points(
                PLUGIN_ENTRY_POINT_GROUP, the_manager_plugin_module_hook
            )
            is True
        )
        assert a_plugin_system.identifiers() == [entry_point_plugin_identifier]

    def test_when_entry_point_plugin_identifier_already_used_then_skipped(
        self,
        the_manager_plugin_module_hook,
        an_entry_point_package_plugin_root,
        entry_point_plugin_identifier,
        mock_logger,
        monkeypatch,
    ):
        # setup

        plugin_system = PythonPluginSystem(mock_logger)
        monkeypatch.syspath_prepend(an_entry_point_package_plugin_root)

        # Register a plugin that conflicts with the plugin discovered
        # at the entry point.
        class ExpectedPlugin(PythonPluginSystemPlugin):
            @classmethod
            def identifier(cls):
                return entry_point_plugin_identifier

        plugin_system.register(ExpectedPlugin, "/some/plugin/path")

        # action

        plugin_system.scan_entry_points(PLUGIN_ENTRY_POINT_GROUP, the_manager_plugin_module_hook)

        # confirm

        actual_plugin = plugin_system.plugin(entry_point_plugin_identifier)
        assert actual_plugin is ExpectedPlugin

        entry_point_plugin_init = os.path.join(
            an_entry_point_package_plugin_root, "packaged_plugin", "__init__.py"
        )
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"PythonPluginSystem: Skipping class"
            f" '<class 'packaged_plugin.PackagePlugin.PackagePlugin'>' defined in"
            f" '{entry_point_plugin_init}'. Already registered by '/some/plugin/path'",
        )

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, the_manager_plugin_module_hook, broken_python_plugins_path, mock_logger, monkeypatch
    ):
        monkeypatch.syspath_prepend(broken_python_plugins_path)

        plugin_system = PythonPluginSystem(mock_logger)
        plugin_system.scan_entry_points(PLUGIN_ENTRY_POINT_GROUP, the_manager_plugin_module_hook)

        assert not plugin_system.identifiers()
        # mock_logger.mock.log.assert_called_once()
        missing_plugin_path = os.path.join(broken_python_plugins_path, "missing_plugin.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            f"PythonPluginSystem: No top-level 'openassetioPlugin' variable {missing_plugin_path}",
        )
        raises_exception_path = os.path.join(broken_python_plugins_path, "raises_exception.py")
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kError,
            StringContaining(
                [
                    "PythonPluginSystem: Caught exception loading raies_exception:\n",
                    f'  File "{raises_exception_path}", line 5, in <module>\n',
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


@pytest.fixture
def a_plugin_system_with_mocked_scanning(mock_logger, monkeypatch):
    plugin_system = PythonPluginSystem(mock_logger)
    monkeypatch.setattr(
        plugin_system, "scan_paths", mock.create_autospec(spec=plugin_system.scan_paths)
    )
    monkeypatch.setattr(
        plugin_system,
        "scan_entry_points",
        mock.create_autospec(spec=plugin_system.scan_entry_points),
    )
    return plugin_system


# We use a real logger vs a mock, as it makes debugging test failures
# easier as it surfaces any actual in-flight errors from the plugin
# system.
@pytest.fixture
def a_logger():
    return ConsoleLogger()


@pytest.fixture
def a_paths_env_var():
    return "test_pythonpluginsystem_PATHS_ENV_VAR"


@pytest.fixture
def a_disable_entry_point_env_var():
    return "test_pythonpluginsystem_DISABLE_ENTRY_POINT_ENV_VAR"


@pytest.fixture
def an_entry_point_group_name():
    return "some_entry_point"


@pytest.fixture
def a_module_hook_name():
    return "some_hook"


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
