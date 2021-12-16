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
These tests check the functionality of the plugin system.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
from unittest import mock

import pytest

from openassetio.logging import LoggerInterface
from openassetio.pluginSystem import PluginSystemManagerFactory


@pytest.fixture
def a_logger():
    return mock.create_autospec(spec=LoggerInterface)


# Using a fixture here to make it easier to hoist to a
# higher level later, if needed by other tests.
@pytest.fixture
def plugin_path_var_name():
    return "OPENASSETIO_PLUGIN_PATH"


class Test_PluginSystemManagerFactory_init:

    def test_when_env_var_not_set_then_logs_warning(
            self, a_logger, plugin_path_var_name, monkeypatch):

        expected_msg = f"{plugin_path_var_name} is not set. " \
                       "It is somewhat unlikely that you will find any plugins..."
        expected_severity = a_logger.kWarning

        if plugin_path_var_name in os.environ:
            monkeypatch.delenv(plugin_path_var_name)

        factory = PluginSystemManagerFactory(a_logger)
        # Plugins are scanned lazily when first requested
        _ = factory.identifiers()
        a_logger.log.assert_called_once_with(expected_msg, expected_severity)


class Test_PluginSystemManagerFactory_identifiers:

    def test_when_env_var_not_set_returns_empty_list(
            self, a_logger, plugin_path_var_name, monkeypatch):

        if plugin_path_var_name in os.environ:
            monkeypatch.delenv(plugin_path_var_name)

        factory = PluginSystemManagerFactory(a_logger)
        assert factory.identifiers() == []

    def test_when_env_var_empty_returns_empty_list(
            self, a_logger, plugin_path_var_name, monkeypatch):

        expected_identifiers = []

        plugin_paths = ""
        monkeypatch.setenv(plugin_path_var_name, plugin_paths)

        factory = PluginSystemManagerFactory(a_logger)
        assert factory.identifiers() == expected_identifiers
