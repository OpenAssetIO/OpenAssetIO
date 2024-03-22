#
#   Copyright 2013-2024 The Foundry Visionmongers Ltd
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

import os

from openassetio.pluginSystem import CppPluginSystemManagerImplementationFactory


lib_ext = "so" if os.name == "posix" else "dll"


class Test_CppPluginSystemManagerImplementationFactory_kPluginEnvVar:
    def test_exposes_plugin_path_var_name_with_expected_value(self):
        assert (
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar == "OPENASSETIO_PLUGIN_PATH"
        )


class Test_CppPluginSystemManagerImplementationFactory:
    def test_when_no_paths_then_warning_logged(self, mock_logger, monkeypatch):
        expected_msg = (
            "No search paths specified, no plugins will load - check"
            f" ${CppPluginSystemManagerImplementationFactory.kPluginEnvVar} is set"
        )
        expected_severity = mock_logger.Severity.kWarning

        monkeypatch.delenv(
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar, raising=False
        )
        factory = CppPluginSystemManagerImplementationFactory(mock_logger)
        # Plugins are scanned lazily when first requested
        assert factory.identifiers() == []
        mock_logger.mock.log.assert_called_once_with(expected_severity, expected_msg)

    def test_when_no_args_and_path_env_then_path_plugins_loaded(
        self,
        a_cpp_plugin_path,
        plugin_a_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar,
            a_cpp_plugin_path,
        )
        factory = CppPluginSystemManagerImplementationFactory(mock_logger)
        assert factory.identifiers() == [plugin_a_identifier]

    def test_when_path_arg_set_then_overrides_path_env(
        self,
        the_cpp_plugins_root_path,
        plugin_b_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar,
            os.path.join(the_cpp_plugins_root_path, "pathA"),
        )

        factory = CppPluginSystemManagerImplementationFactory(
            paths=os.path.join(the_cpp_plugins_root_path, "pathB"), logger=mock_logger
        )
        assert factory.identifiers() == [
            plugin_b_identifier,
        ]

    def test_when_paths_empty_then_returns_empty_list(self, mock_logger):
        plugin_paths = ""
        factory = CppPluginSystemManagerImplementationFactory(
            paths=plugin_paths, logger=mock_logger
        )
        assert factory.identifiers() == []

    def test_when_non_manager_plugin_then_logs_warning(
        self, the_cpp_plugins_root_path, mock_logger
    ):
        # TODO(DF): Create this test plugin.
        a_non_manager_plugin_path = os.path.join(the_cpp_plugins_root_path, "not-a-manager")
        a_non_manager_plugin_file_path = os.path.join(a_non_manager_plugin_path, f"not-a-manager.{lib_ext}")
        a_non_manager_plugin_identifier = (
            "org.openassetio.test.pluginSystem.resources.not-a-manager"
        )
        factory = CppPluginSystemManagerImplementationFactory(
            a_non_manager_plugin_path, mock_logger
        )

        assert factory.identifiers() == []

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            f"Plugin '{a_non_manager_plugin_identifier}' from '{a_non_manager_plugin_file_path}'"
            " is not a CppPluginSystemManagerPlugin"
        )
