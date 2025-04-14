#
#   Copyright 2025 The Foundry Visionmongers Ltd
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
UIDelegateImplementationFactoryInterface implementation.
"""

# pylint: disable=unused-argument
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison
import sys
from unittest import mock

import pytest

from openassetio.log import ConsoleLogger
from openassetio.ui.pluginSystem import PythonPluginSystemUIDelegateImplementationFactory
from openassetio.pluginSystem import PythonPluginSystem


class Test_PythonPluginSystemUIDelegateImplementationFactory:
    def test_exposes_plugin_path_var_name_with_expected_value(self):
        assert (
            PythonPluginSystemUIDelegateImplementationFactory.kPluginEnvVar
            == "OPENASSETIO_UI_PLUGIN_PATH"
        )

    def test_exposes_disable_entry_points_var_name_with_expected_value(self):
        assert (
            PythonPluginSystemUIDelegateImplementationFactory.kDisableEntryPointsEnvVar
            == "OPENASSETIO_UI_DISABLE_ENTRYPOINTS_PLUGINS"
        )

    def test_exposes_entry_point_group_with_expected_value(self):
        assert (
            PythonPluginSystemUIDelegateImplementationFactory.kPackageEntryPointGroup
            == "openassetio.ui_plugin"
        )

    def test_exposes_module_hook_with_expected_value(self):
        assert (
            PythonPluginSystemUIDelegateImplementationFactory.kModuleHookName
            == "openassetioUIPlugin"
        )


class Test_PythonPluginSystemUIDelegateImplementationFactory_init:
    def test_when_no_paths_then_paths_not_scanned(self, mock_plugin_system):
        factory = PythonPluginSystemUIDelegateImplementationFactory(ConsoleLogger())

        factory.identifiers()

        mock_plugin_system.scan.assert_called_once_with(
            None,
            PythonPluginSystemUIDelegateImplementationFactory.kPluginEnvVar,
            PythonPluginSystemUIDelegateImplementationFactory.kPackageEntryPointGroup,
            PythonPluginSystemUIDelegateImplementationFactory.kDisableEntryPointsEnvVar,
            None,
            PythonPluginSystemUIDelegateImplementationFactory.kModuleHookName,
        )

    def test_when_paths_then_paths_scanned(self, mock_plugin_system):
        factory = PythonPluginSystemUIDelegateImplementationFactory(
            ConsoleLogger(), paths="/some/path"
        )

        factory.identifiers()

        mock_plugin_system.scan.assert_called_once_with(
            "/some/path",
            PythonPluginSystemUIDelegateImplementationFactory.kPluginEnvVar,
            PythonPluginSystemUIDelegateImplementationFactory.kPackageEntryPointGroup,
            PythonPluginSystemUIDelegateImplementationFactory.kDisableEntryPointsEnvVar,
            None,
            PythonPluginSystemUIDelegateImplementationFactory.kModuleHookName,
        )

    def test_when_entry_points_disabled_arg_then_arg_passed_to_plugin_system(
        self, mock_plugin_system
    ):
        disable_entry_points = mock.Mock()

        factory = PythonPluginSystemUIDelegateImplementationFactory(
            ConsoleLogger(), disableEntryPointsPlugins=disable_entry_points
        )

        factory.identifiers()

        mock_plugin_system.scan.assert_called_once_with(
            None,
            PythonPluginSystemUIDelegateImplementationFactory.kPluginEnvVar,
            PythonPluginSystemUIDelegateImplementationFactory.kPackageEntryPointGroup,
            PythonPluginSystemUIDelegateImplementationFactory.kDisableEntryPointsEnvVar,
            disable_entry_points,
            PythonPluginSystemUIDelegateImplementationFactory.kModuleHookName,
        )


class Test_PythonPluginSystemUIDelegateImplementationFactory_identifiers:
    def test_lazy_scans_for_plugins_before_returning_identifiers(
        self, mock_plugin_system, mock_logger
    ):
        factory = PythonPluginSystemUIDelegateImplementationFactory(mock_logger)
        calls = mock.Mock()
        calls.attach_mock(mock_plugin_system.scan, "scan")
        calls.attach_mock(mock_plugin_system.identifiers, "identifiers")

        first_identifiers = factory.identifiers()
        second_identifiers = factory.identifiers()

        assert calls.method_calls == [
            mock.call.scan(mock.ANY, mock.ANY, mock.ANY, mock.ANY, mock.ANY, mock.ANY),
            mock.call.identifiers(),
            mock.call.identifiers(),
        ]
        assert first_identifiers == second_identifiers
        assert first_identifiers == mock_plugin_system.identifiers.return_value


class Test_PythonPluginSystemUIDelegateImplementationFactory_instantiate:
    def test_lazy_scans_for_plugins_before_instantiating(self, mock_plugin_system, mock_logger):
        factory = PythonPluginSystemUIDelegateImplementationFactory(mock_logger)
        calls = mock.Mock()
        calls.attach_mock(mock_plugin_system.scan, "scan")
        calls.attach_mock(mock_plugin_system.plugin, "plugin")

        factory.instantiate("first_id")
        factory.instantiate("second_id")

        assert calls.method_calls == [
            mock.call.scan(mock.ANY, mock.ANY, mock.ANY, mock.ANY, mock.ANY, mock.ANY),
            mock.call.plugin("first_id"),
            mock.call.plugin("second_id"),
        ]

    def test_returns_instance_created_by_plugin(self, mock_plugin_system, mock_logger):
        factory = PythonPluginSystemUIDelegateImplementationFactory(mock_logger)

        instance = factory.instantiate("some_identifier")

        mock_plugin_system.plugin.assert_called_once_with("some_identifier")
        mock_plugin_system.plugin.return_value.interface.assert_called_once_with()
        assert instance is mock_plugin_system.plugin.return_value.interface.return_value


@pytest.fixture
def mock_plugin_system(monkeypatch):
    plugin_system = mock.create_autospec(spec=PythonPluginSystem)
    monkeypatch.setattr(
        sys.modules[PythonPluginSystemUIDelegateImplementationFactory.__module__],
        "PythonPluginSystem",
        plugin_system,
    )
    return plugin_system.return_value
