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

import os
import re

import pytest

from openassetio import errors
from openassetio.ui.pluginSystem import CppPluginSystemUIDelegateImplementationFactory


class Test_CppPluginSystemUIDelegateImplementationFactory_kPluginEnvVar:
    def test_exposes_plugin_path_var_name_with_expected_value(self):
        assert (
            CppPluginSystemUIDelegateImplementationFactory.kPluginEnvVar
            == "OPENASSETIO_UI_PLUGIN_PATH"
        )


class Test_CppPluginSystemUIDelegateImplementationFactory_kModuleHookName:
    def test_exposes_module_hook_name_with_expected_value(self):
        assert (
            CppPluginSystemUIDelegateImplementationFactory.kModuleHookName == "openassetioUIPlugin"
        )


class Test_CppPluginSystemUIDelegateImplementationFactory_lazy_scanning:
    def test_when_no_paths_then_warning_logged(self, mock_logger, monkeypatch):
        expected_msg = (
            "No search paths specified, no plugins will load - check"
            f" ${CppPluginSystemUIDelegateImplementationFactory.kPluginEnvVar} is set"
        )
        expected_severity = mock_logger.Severity.kWarning

        monkeypatch.delenv(
            CppPluginSystemUIDelegateImplementationFactory.kPluginEnvVar, raising=False
        )
        factory = CppPluginSystemUIDelegateImplementationFactory(mock_logger)
        # Plugins are scanned lazily when first requested
        assert factory.identifiers() == []

        mock_logger.mock.log.assert_called_once_with(expected_severity, expected_msg)

    def test_when_no_args_and_path_env_then_path_plugins_loaded(
        self,
        a_cpp_ui_delegate_plugin_path,
        plugin_a_identifier,
        mock_logger,
        monkeypatch,
    ):
        monkeypatch.setenv(
            CppPluginSystemUIDelegateImplementationFactory.kPluginEnvVar,
            a_cpp_ui_delegate_plugin_path,
        )
        factory = CppPluginSystemUIDelegateImplementationFactory(mock_logger)
        assert factory.identifiers() == [plugin_a_identifier]

    def test_when_paths_empty_then_returns_empty_list(self, mock_logger):
        plugin_paths = ""
        factory = CppPluginSystemUIDelegateImplementationFactory(
            paths=plugin_paths, logger=mock_logger
        )
        assert factory.identifiers() == []


class Test_CppPluginSystemUIDelegateImplementationFactory_identifiers:
    def test_when_non_ui_delegate_plugin_then_logs_warning(
        self, a_cpp_plugin_path, mock_logger, regex_matcher
    ):
        expected_log_message_suffix = (
            "It is not a UI delegate plugin (CppPluginSystemUIDelegatePlugin)."
        )

        factory = CppPluginSystemUIDelegateImplementationFactory(a_cpp_plugin_path, mock_logger)

        assert factory.identifiers() == []

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            regex_matcher(re.escape(expected_log_message_suffix) + "$"),
        )


class Test_CppPluginSystemUIDelegateImplementationFactory_instantiate:
    def test_when_non_ui_delegate_plugin_then_raises_InputValidationException(
        self, a_cpp_plugin_path, plugin_a_identifier, mock_logger, regex_matcher
    ):
        factory = CppPluginSystemUIDelegateImplementationFactory(a_cpp_plugin_path, mock_logger)

        with pytest.raises(errors.InputValidationException):
            factory.instantiate(plugin_a_identifier)

        expected_log_message_suffix = (
            "It is not a UI delegate plugin (CppPluginSystemUIDelegatePlugin)."
        )
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kWarning,
            regex_matcher(re.escape(expected_log_message_suffix) + "$"),
        )

    def test_when_plugin_found_then_returns_instantiated_ui_delegate_implementation(
        self, a_cpp_ui_delegate_plugin_path, plugin_a_identifier, mock_logger
    ):
        factory = CppPluginSystemUIDelegateImplementationFactory(
            a_cpp_ui_delegate_plugin_path, mock_logger
        )

        ui_delegate_interface = factory.instantiate(plugin_a_identifier)

        assert ui_delegate_interface.identifier() == plugin_a_identifier

    def test_when_plugin_throws_exception_then_exception_can_be_caught(
        self, a_cpp_ui_delegate_plugin_path, plugin_a_identifier, mock_logger
    ):
        # Confidence check that RTTI is working.

        factory = CppPluginSystemUIDelegateImplementationFactory(
            a_cpp_ui_delegate_plugin_path, mock_logger
        )
        ui_delegate_interface = factory.instantiate(plugin_a_identifier)

        # See StubUIDelegateInterface - the `info()` method is overridden
        # to throw an OpenAssetIO-specific exception.
        with pytest.raises(errors.NotImplementedException, match="Stub doesn't support info"):
            ui_delegate_interface.info()


class Test_UIDelegateFactory_CppPluginSystemUIDelegateImplementationFactory:
    def test(
        self,
        a_cpp_ui_delegate_plugin_path,
        plugin_a_identifier,
        mock_logger,
        mock_host_interface,
        monkeypatch,
    ):
        # Confidence check that UIDelegateFactory works with
        # CppPluginSystemUIDelegateImplementationFactory.

        # TODO(DF): fill in details when UIDelegateFactory available
        pass


@pytest.fixture
def a_cpp_ui_delegate_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "ui", "uiA")


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
