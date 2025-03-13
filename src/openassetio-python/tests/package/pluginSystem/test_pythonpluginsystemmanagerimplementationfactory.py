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
These tests check the functionality of the plugin system based
ManagerImplementationFactoryInterface implementation.
"""

# pylint: disable=unused-argument
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

import pytest

from openassetio.log import ConsoleLogger
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory


class Test_PythonPluginSystemManagerImplementationFactory:
    def test_exposes_plugin_path_var_name_with_expected_value(self):
        assert (
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar
            == "OPENASSETIO_PLUGIN_PATH"
        )

    def test_exposes_disable_entry_points_var_name_with_expected_value(self):
        assert (
            PythonPluginSystemManagerImplementationFactory.kDisableEntryPointsEnvVar
            == "OPENASSETIO_DISABLE_ENTRYPOINTS_PLUGINS"
        )

    def test_exposes_entry_point_group_with_expected_value(self):
        assert (
            PythonPluginSystemManagerImplementationFactory.kPackageEntryPointGroup
            == "openassetio.manager_plugin"
        )

    def test_exposes_module_hook_with_expected_value(self):
        assert (
            PythonPluginSystemManagerImplementationFactory.kModuleHookName == "openassetioPlugin"
        )


class Test_PythonPluginSystemManagerImplementationFactory_init:
    def test_when_no_args_or_env_vars_then_entry_point_plugins_loaded(
        self,
        prepended_sys_path_with_entry_point_plugin,
        entry_point_plugin_identifier,
    ):
        factory = PythonPluginSystemManagerImplementationFactory(ConsoleLogger())
        assert factory.identifiers() == [entry_point_plugin_identifier]

    def test_when_no_paths_and_entry_points_disabled_then_warning_logged(
        self, mock_logger, monkeypatch
    ):
        expected_msg = (
            "No search paths specified and entry point plugins are disabled, no plugins will "
            f"load - check ${PythonPluginSystemManagerImplementationFactory.kPluginEnvVar} is set."
        )
        expected_severity = mock_logger.Severity.kWarning

        monkeypatch.delenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar, raising=False
        )

        factory = PythonPluginSystemManagerImplementationFactory(
            mock_logger, disableEntryPointsPlugins=True
        )
        # Plugins are scanned lazily when first requested
        assert factory.identifiers() == []
        mock_logger.mock.log.assert_called_once_with(expected_severity, expected_msg)

    def test_when_no_args_and_entry_points_disabled_env_then_entry_point_not_loaded(
        self, prepended_sys_path_with_entry_point_plugin, monkeypatch
    ):
        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kDisableEntryPointsEnvVar, "1"
        )
        monkeypatch.delenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar, raising=False
        )

        factory = PythonPluginSystemManagerImplementationFactory(ConsoleLogger())
        assert factory.identifiers() == []

    def test_when_no_args_and_path_env_then_path_plugins_loaded(
        self,
        a_python_module_plugin_path,
        plugin_a_identifier,
        monkeypatch,
    ):
        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar,
            a_python_module_plugin_path,
        )
        factory = PythonPluginSystemManagerImplementationFactory(ConsoleLogger())
        assert factory.identifiers() == [plugin_a_identifier]

    def test_when_path_arg_set_then_overrides_path_env(
        self,
        a_python_module_plugin_path,
        a_python_package_plugin_path,
        plugin_b_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar,
            a_python_module_plugin_path,
        )

        factory = PythonPluginSystemManagerImplementationFactory(
            paths=a_python_package_plugin_path, logger=mock_logger
        )
        assert factory.identifiers() == [
            plugin_b_identifier,
        ]

    def test_when_entry_points_disable_arg_set_then_overrides_entry_points_disable_env(
        self,
        prepended_sys_path_with_entry_point_plugin,
        entry_point_plugin_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kDisableEntryPointsEnvVar, "1"
        )
        factory = PythonPluginSystemManagerImplementationFactory(
            disableEntryPointsPlugins=False, logger=mock_logger
        )
        assert factory.identifiers() == [
            entry_point_plugin_identifier,
        ]

    def test_when_paths_empty_then_returns_empty_list(self, mock_logger):

        plugin_paths = ""
        factory = PythonPluginSystemManagerImplementationFactory(
            paths=plugin_paths, logger=mock_logger
        )
        assert factory.identifiers() == []

    def test_when_duplicate_identifiers_path_selected_over_entry_point(
        self,
        prepended_sys_path_with_entry_point_plugin,
        a_python_package_plugin_path,
        plugin_b_identifier,
        mock_logger,
    ):
        factory = PythonPluginSystemManagerImplementationFactory(
            mock_logger, paths=a_python_package_plugin_path, disableEntryPointsPlugins=False
        )

        assert factory.identifiers() == [
            plugin_b_identifier,
        ]
        assert a_python_package_plugin_path in factory.instantiate(plugin_b_identifier)["file"]


@pytest.fixture
def prepended_sys_path_with_entry_point_plugin(an_entry_point_package_plugin_root, monkeypatch):
    monkeypatch.syspath_prepend(an_entry_point_package_plugin_root)
