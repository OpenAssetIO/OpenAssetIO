#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
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
from pathlib import PurePath

import pytest

from openassetio.pluginSystem import PluginSystemManagerImplementationFactory

#
# Plugin fixtures
#
# These provide information about expected plugins within the source
# tree. We use fixtures for this, over variables to make it easier to
# hoist to a higher level later, if needed by other tests.
#
# {


@pytest.fixture
def plugin_path_var_name():
    """
    Provides the name of the environment variable that controls the
    default search paths in the PluginSystem.
    """
    return "OPENASSETIO_PLUGIN_PATH"


@pytest.fixture
def local_plugin_path():
    """
    Provides a suitable PluginSystem search path that includes plugins
    provided by the project.
    """
    test_path = PurePath(__file__)
    root_dir = test_path.parents[4]
    examples_dir = root_dir / "resources" / "examples" / "manager"
    return str(examples_dir / "SampleAssetManager" / "python")


@pytest.fixture
def local_plugin_identifiers():
    """
    Provides a list of the expected identifiers of plugins discovered
    when using those provided by local_plugin_path
    """
    return [
        "org.openassetio.examples.manager.sam",
    ]


#
# }
#


class Test_PluginSystemManagerImplementationFactory_init:
    def test_plugin_factory_uses_the_expected_env_var(self):
        assert PluginSystemManagerImplementationFactory.kPluginEnvVar == "OPENASSETIO_PLUGIN_PATH"

    def test_when_env_var_not_set_then_logs_warning(self, mock_logger, monkeypatch):

        expected_msg = (
            f"{PluginSystemManagerImplementationFactory.kPluginEnvVar} is not set. "
            "It is somewhat unlikely that you will find any plugins..."
        )
        expected_severity = mock_logger.kWarning

        if PluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PluginSystemManagerImplementationFactory(mock_logger)
        # Plugins are scanned lazily when first requested
        _ = factory.identifiers()
        mock_logger.mock.log.assert_called_once_with(expected_severity, expected_msg)


class Test_PluginSystemManagerImplementationFactory_identifiers:
    def test_when_env_var_not_set_then_returns_empty_list(self, mock_logger, monkeypatch):

        if PluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PluginSystemManagerImplementationFactory(mock_logger)
        identifiers = factory.identifiers()
        # Check it is an empty list, not None, or any other value
        # that would satisty == [] as a boolean comparison.
        assert isinstance(identifiers, list)
        assert len(identifiers) == 0

    def test_when_env_var_empty_then_returns_empty_list(self, mock_logger, monkeypatch):

        plugin_paths = ""
        monkeypatch.setenv(PluginSystemManagerImplementationFactory.kPluginEnvVar, plugin_paths)

        factory = PluginSystemManagerImplementationFactory(mock_logger)
        identifiers = factory.identifiers()
        assert isinstance(identifiers, list)
        assert len(identifiers) == 0

    def test_when_env_var_set_to_local_plugin_path_then_finds_local_plugins(
        self, mock_logger, local_plugin_path, local_plugin_identifiers, monkeypatch
    ):

        monkeypatch.setenv(
            PluginSystemManagerImplementationFactory.kPluginEnvVar, local_plugin_path
        )

        factory = PluginSystemManagerImplementationFactory(mock_logger)
        assert factory.identifiers() == local_plugin_identifiers

    def test_when_paths_set_to_local_plugin_path_then_finds_local_plugins(
        self, mock_logger, local_plugin_path, local_plugin_identifiers, monkeypatch
    ):

        if PluginSystemManagerImplementationFactory.kPluginEnvVar in os.environ:
            monkeypatch.delenv(PluginSystemManagerImplementationFactory.kPluginEnvVar)

        factory = PluginSystemManagerImplementationFactory(mock_logger, paths=local_plugin_path)
        assert factory.identifiers() == local_plugin_identifiers

    def test_when_env_var_overridden_to_local_plugin_path_then_finds_local_plugins(
        self, mock_logger, local_plugin_path, local_plugin_identifiers, monkeypatch
    ):

        monkeypatch.setenv(
            PluginSystemManagerImplementationFactory.kPluginEnvVar, "some invalid value"
        )

        factory = PluginSystemManagerImplementationFactory(mock_logger, paths=local_plugin_path)
        assert factory.identifiers() == local_plugin_identifiers
