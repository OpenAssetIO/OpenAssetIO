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

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os

from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory


class Test_PythonPluginSystemManagerImplementationFactory_init:
    def test_plugin_factory_uses_the_expected_env_var(self):
        assert (
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar
            == "OPENASSETIO_PLUGIN_PATH"
        )

    def test_when_env_var_not_set_then_logs_warning(self, mock_logger, monkeypatch):
        expected_msg = (
            f"{PythonPluginSystemManagerImplementationFactory.kPluginEnvVar} is not set. "
            "It is somewhat unlikely that you will find any plugins..."
        )
        expected_severity = mock_logger.Severity.kWarning

        if PythonPluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PythonPluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PythonPluginSystemManagerImplementationFactory(mock_logger)
        # Plugins are scanned lazily when first requested
        _ = factory.identifiers()
        mock_logger.mock.log.assert_called_once_with(expected_severity, expected_msg)


class Test_PythonPluginSystemManagerImplementationFactory_identifiers:
    def test_when_env_var_not_set_then_returns_empty_list(self, mock_logger, monkeypatch):

        if PythonPluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PythonPluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PythonPluginSystemManagerImplementationFactory(mock_logger)
        identifiers = factory.identifiers()
        # Check it is an empty list, not None, or any other value
        # that would satisty == [] as a boolean comparison.
        assert isinstance(identifiers, list)
        assert len(identifiers) == 0

    def test_when_env_var_empty_then_returns_empty_list(self, mock_logger, monkeypatch):

        plugin_paths = ""
        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar, plugin_paths
        )

        factory = PythonPluginSystemManagerImplementationFactory(mock_logger)
        identifiers = factory.identifiers()
        assert isinstance(identifiers, list)
        assert len(identifiers) == 0

    def test_when_env_var_set_to_plugin_path_then_finds_plugins(
        self, mock_logger, a_package_plugin_path, package_plugin_identifier, monkeypatch
    ):

        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar, a_package_plugin_path
        )

        factory = PythonPluginSystemManagerImplementationFactory(mock_logger)
        assert factory.identifiers() == [package_plugin_identifier,]

    def test_when_paths_set_to_a_package_plugin_path_then_finds_local_plugins(
        self, mock_logger, a_package_plugin_path, package_plugin_identifier, monkeypatch
    ):

        if PythonPluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PythonPluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PythonPluginSystemManagerImplementationFactory(
            mock_logger, paths=a_package_plugin_path
        )
        assert factory.identifiers() == [package_plugin_identifier,]

    def test_when_env_var_overridden_to_a_package_plugin_path_then_finds_local_plugins(
        self, mock_logger, a_package_plugin_path, package_plugin_identifier, monkeypatch
    ):

        monkeypatch.setenv(
            PythonPluginSystemManagerImplementationFactory.kPluginEnvVar, "some invalid value"
        )

        factory = PythonPluginSystemManagerImplementationFactory(
            mock_logger, paths=a_package_plugin_path
        )
        assert factory.identifiers() == [package_plugin_identifier,]
