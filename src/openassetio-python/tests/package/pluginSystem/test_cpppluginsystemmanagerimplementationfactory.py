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
These tests check the functionality of the plugin system based
ManagerImplementationFactoryInterface implementation.
"""
# pylint: disable=unused-argument
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

import os
import re

import pytest

from openassetio import errors
from openassetio.hostApi import ManagerFactory
from openassetio.pluginSystem import CppPluginSystemManagerImplementationFactory


lib_ext = "so" if os.name == "posix" else "dll"


class Test_CppPluginSystemManagerImplementationFactory_kPluginEnvVar:
    def test_exposes_plugin_path_var_name_with_expected_value(self):
        assert (
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar == "OPENASSETIO_PLUGIN_PATH"
        )


class Test_CppPluginSystemManagerImplementationFactory_kModuleHookName:
    def test_exposes_module_hook_name_with_expected_value(self):
        assert CppPluginSystemManagerImplementationFactory.kModuleHookName == "openassetioPlugin"


class Test_CppPluginSystemManagerImplementationFactory_lazy_scanning:
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
        a_cpp_manager_plugin_path,
        plugin_a_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar,
            a_cpp_manager_plugin_path,
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
            os.path.join(the_cpp_plugins_root_path, "managerA"),
        )

        factory = CppPluginSystemManagerImplementationFactory(
            paths=os.path.join(the_cpp_plugins_root_path, "managerB"), logger=mock_logger
        )
        assert factory.identifiers() == [plugin_b_identifier]

    def test_when_paths_empty_then_returns_empty_list(self, mock_logger):
        plugin_paths = ""
        factory = CppPluginSystemManagerImplementationFactory(
            paths=plugin_paths, logger=mock_logger
        )
        assert factory.identifiers() == []


class Test_CppPluginSystemManagerImplementationFactory_identifiers:
    def test_when_non_manager_plugin_then_logs_warning(
        self, a_cpp_plugin_path, mock_logger, regex_matcher
    ):
        expected_log_message_suffix = "It is not a manager plugin (CppPluginSystemManagerPlugin)."

        factory = CppPluginSystemManagerImplementationFactory(a_cpp_plugin_path, mock_logger)

        assert factory.identifiers() == []

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            regex_matcher(re.escape(expected_log_message_suffix) + "$"),
        )


class Test_CppPluginSystemManagerImplementationFactory_instantiate:
    def test_when_non_manager_plugin_then_raises_InputValidationException(
        self, a_cpp_plugin_path, plugin_a_identifier, mock_logger, regex_matcher
    ):
        factory = CppPluginSystemManagerImplementationFactory(a_cpp_plugin_path, mock_logger)

        with pytest.raises(errors.InputValidationException):
            factory.instantiate(plugin_a_identifier)

        expected_log_message_suffix = "It is not a manager plugin (CppPluginSystemManagerPlugin)."
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            regex_matcher(re.escape(expected_log_message_suffix) + "$"),
        )

    def test_when_plugin_found_then_returns_instantiated_manager_implementation(
        self, a_cpp_manager_plugin_path, plugin_a_identifier, mock_logger
    ):
        factory = CppPluginSystemManagerImplementationFactory(
            a_cpp_manager_plugin_path, mock_logger
        )

        manager_interface = factory.instantiate(plugin_a_identifier)

        assert manager_interface.identifier() == plugin_a_identifier

    def test_when_plugin_throws_exception_then_exception_can_be_caught(
        self, a_cpp_manager_plugin_path, plugin_a_identifier, mock_logger
    ):
        # Confidence check that RTTI is working.

        factory = CppPluginSystemManagerImplementationFactory(
            a_cpp_manager_plugin_path, mock_logger
        )
        manager_interface = factory.instantiate(plugin_a_identifier)

        # See StubManagerInterface - the `info()` method is overridden
        # to throw an OpenAssetIO-specific exception.
        with pytest.raises(errors.NotImplementedException, match="Stub doesn't support info"):
            manager_interface.info()


class Test_ManagerFactory_CppPluginSystemManagerImplementationFactory:
    def test(
        self,
        a_cpp_manager_plugin_path,
        plugin_a_identifier,
        mock_logger,
        mock_host_interface,
        monkeypatch,
    ):
        # Confidence check that ManagerFactory works with
        # CppPluginSystemManagerImplementationFactory.

        monkeypatch.setenv(
            CppPluginSystemManagerImplementationFactory.kPluginEnvVar,
            a_cpp_manager_plugin_path,
        )

        manager_factory = ManagerFactory(
            mock_host_interface,
            CppPluginSystemManagerImplementationFactory(mock_logger),
            mock_logger,
        )

        manager = manager_factory.createManager(plugin_a_identifier)

        assert manager.identifier() == plugin_a_identifier


@pytest.fixture(scope="module", autouse=True)
def skip_if_no_test_plugins_available(the_cpp_plugins_root_path):
    """
    Skip tests in this module if there are no plugins to test against.

    Some test runs may genuinely not have access to the plugins, e.g.
    when building/testing Python wheels, since the test plugins are
    created by CMake when test targets are enabled. In this case, skip
    the tests in this module.

    If we know we are running via CTest (i.e.
    OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR is defined), then the test
    plugins should definitely exist. So in this case, ensure we do _not_
    disable these tests.
    """
    if (
        not os.path.isdir(the_cpp_plugins_root_path)
        and os.environ.get("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR") is None
    ):
        pytest.skip("Skipping C++ plugin system tests as no test plugins are available")
