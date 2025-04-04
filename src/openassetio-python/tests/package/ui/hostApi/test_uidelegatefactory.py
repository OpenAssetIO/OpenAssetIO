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
Tests that cover the openassetio.ui.hostApi.UIDelegateFactory class.

Note that these tests are almost identical to the
openassetio.hostApi.ManagerFactory tests.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import os
import pathlib
from unittest import mock

import pytest

from openassetio import errors
from openassetio.ui.hostApi import (
    UIDelegateFactory,
    UIDelegate,
    UIDelegateImplementationFactoryInterface,
)
from openassetio.log import LoggerInterface


class Test_UIDelegateFactory_UIDelegateDetail_equality:
    def test_when_other_is_equal_then_compares_equal(self):
        ui_delegate_details = UIDelegateFactory.UIDelegateDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )
        other_ui_delegate_detail = UIDelegateFactory.UIDelegateDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )

        assert ui_delegate_details == other_ui_delegate_detail

    @pytest.mark.parametrize(
        "other_ui_delegate_detail",
        [
            UIDelegateFactory.UIDelegateDetail(identifier="z", displayName="b", info={"c": "d"}),
            UIDelegateFactory.UIDelegateDetail(identifier="a", displayName="z", info={"c": "d"}),
            UIDelegateFactory.UIDelegateDetail(identifier="a", displayName="b", info={"c": "z"}),
        ],
    )
    def test_when_other_has_unequal_field_then_object_compares_unequal(
        self, other_ui_delegate_detail
    ):
        ui_delegate_details = UIDelegateFactory.UIDelegateDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )

        assert ui_delegate_details != other_ui_delegate_detail


class Test_UIDelegateFactory_identifiers:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_implementation_factory, a_ui_delegate_factory
    ):
        expected = ["first.identifier", "second.identifier"]
        mock_ui_delegate_implementation_factory.mock.identifiers.return_value = expected

        actual = a_ui_delegate_factory.identifiers()

        assert actual == expected


class Test_UIDelegateFactory_availableUIDelegates:
    def test_when_no_implemetations_then_reports_no_implemetation_detais(
        self, mock_ui_delegate_implementation_factory, a_ui_delegate_factory
    ):
        mock_ui_delegate_implementation_factory.mock.identifiers.return_value = []
        mock_ui_delegate_implementation_factory.mock.instantiate.side_effect = []

        expected = {}

        # action

        actual = a_ui_delegate_factory.availableUIDelegates()

        # confirm

        assert actual == expected

    def test_when_has_implementations_then_reports_implementation_details(
        self,
        create_mock_ui_delegate_interface,
        mock_ui_delegate_implementation_factory,
        a_ui_delegate_factory,
    ):
        # setup

        identifiers = ["first.identifier", "second.identifier"]
        mock_ui_delegate_implementation_factory.mock.identifiers.return_value = identifiers

        first_ui_delegate_interface = create_mock_ui_delegate_interface()
        second_ui_delegate_interface = create_mock_ui_delegate_interface()
        first_ui_delegate_interface.mock.identifier.return_value = "first.identifier"
        second_ui_delegate_interface.mock.identifier.return_value = "second.identifier"
        first_ui_delegate_interface.mock.displayName.return_value = "First"
        second_ui_delegate_interface.mock.displayName.return_value = "Second"
        first_ui_delegate_interface.mock.info.return_value = {"first": "info"}
        second_ui_delegate_interface.mock.info.return_value = {"second": "info"}

        mock_ui_delegate_implementation_factory.mock.instantiate.side_effect = [
            first_ui_delegate_interface,
            second_ui_delegate_interface,
        ]

        expected = {
            "first.identifier": UIDelegateFactory.UIDelegateDetail(
                identifier="first.identifier", displayName="First", info={"first": "info"}
            ),
            "second.identifier": UIDelegateFactory.UIDelegateDetail(
                identifier="second.identifier", displayName="Second", info={"second": "info"}
            ),
        }

        # action

        actual = a_ui_delegate_factory.availableUIDelegates()

        # confirm

        assert actual == expected


class Test_UIDelegateFactory_kDefaultUIDelegateConfigEnvVarName:
    def test_has_expected_value(self):
        assert UIDelegateFactory.kDefaultUIDelegateConfigEnvVarName == "OPENASSETIO_DEFAULT_CONFIG"


class Test_UIDelegateFactory_defaultUIDelegateForInterface:
    def test_when_var_not_set_then_returns_none(
        self, mock_ui_delegate_implementation_factory, mock_host_interface, mock_logger
    ):
        assert (
            UIDelegateFactory.defaultUIDelegateForInterface(
                mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
            )
            is None
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_non_existent_path_then_InputValidationException_raised(
        self,
        use_env_var_for_config_file,
        non_existent_ui_delegate_config,  # pylint: disable=unused-argument
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(errors.InputValidationException) as exc:
            if use_env_var_for_config_file:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
                )
            else:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    non_existent_ui_delegate_config,
                    mock_host_interface,
                    mock_ui_delegate_implementation_factory,
                    mock_logger,
                )

        assert (
            str(exc.value) == "Could not load default config from 'i/do/not/exist', file does not"
            " exist."
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_directory_then_InputValidationException_raised(
        self,
        use_env_var_for_config_file,
        directory_ui_delegate_config,  # pylint: disable=unused-argument
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(errors.InputValidationException) as exc:
            if use_env_var_for_config_file:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    mock_host_interface,
                    mock_ui_delegate_implementation_factory,
                    mock_logger,
                )
            else:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    directory_ui_delegate_config,
                    mock_host_interface,
                    mock_ui_delegate_implementation_factory,
                    mock_logger,
                )

        assert (
            str(exc.value)
            == f"Could not load default config from '{directory_ui_delegate_config}', "
            "must be a TOML file not a directory."
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_invalid_format_then_ConfigurationException_raised(
        self,
        use_env_var_for_config_file,
        invalid_ui_delegate_config,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(
            errors.ConfigurationException,
            match=(
                "Error parsing config file. Error while parsing key: multi-line strings are"
                " prohibited in keys"
            ),
        ):
            if use_env_var_for_config_file:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
                )
            else:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    invalid_ui_delegate_config,
                    mock_host_interface,
                    mock_ui_delegate_implementation_factory,
                    mock_logger,
                )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_invalid_property_type_then_ConfigurationException_raised(
        self,
        use_env_var_for_config_file,
        config_with_invalid_property,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(
            errors.ConfigurationException, match="Unsupported value type for 'a_dict'."
        ):
            if use_env_var_for_config_file:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
                )
            else:
                UIDelegateFactory.defaultUIDelegateForInterface(
                    config_with_invalid_property,
                    mock_host_interface,
                    mock_ui_delegate_implementation_factory,
                    mock_logger,
                )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_valid_path_then_expected_ui_delegate_returned_with_expected_settings(
        self,
        use_env_var_for_config_file,
        valid_ui_delegate_config,  # pylint: disable=unused-argument
        resources_dir,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_ui_delegate_interface,
    ):
        expected_host_identifier = "a.host"
        mock_host_interface.mock.identifier.return_value = expected_host_identifier

        expected_ui_delegate_identifier = "identifier.from.toml.file"

        expected_settings = {
            "a_string": "Hello 🐈",
            "a_float": 3.141579,
            "a_bool": False,
            "a_int": 42,
            "a_config_path_twice": f"{resources_dir}/my/🐈/{resources_dir}",
        }

        mock_ui_delegate_interface = create_mock_ui_delegate_interface()
        mock_ui_delegate_interface.mock.identifier.return_value = expected_ui_delegate_identifier

        # Use a side-effect to check host_session as this is constructed
        # privately by the factory.
        def check_initialization(settings, host_session):
            assert settings == expected_settings
            assert host_session.host().identifier() == expected_host_identifier
            return mock.DEFAULT

        mock_ui_delegate_interface.mock.initialize.side_effect = check_initialization

        mock_ui_delegate_implementation_factory.mock.instantiate.return_value = (
            mock_ui_delegate_interface
        )

        if use_env_var_for_config_file:
            ui_delegate = UIDelegateFactory.defaultUIDelegateForInterface(
                mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
            )
        else:
            ui_delegate = UIDelegateFactory.defaultUIDelegateForInterface(
                valid_ui_delegate_config,
                mock_host_interface,
                mock_ui_delegate_implementation_factory,
                mock_logger,
            )

        assert ui_delegate.identifier() == expected_ui_delegate_identifier
        mock_ui_delegate_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_ui_delegate_identifier
        )
        mock_ui_delegate_interface.mock.initialize.assert_called_once()

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_valid_path_then_expected_log_messages_printed(
        self,
        use_env_var_for_config_file,
        valid_ui_delegate_config,  # pylint: disable=unused-argument
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_ui_delegate_interface,
    ):
        mock_ui_delegate_interface = create_mock_ui_delegate_interface()
        mock_ui_delegate_implementation_factory.mock.instantiate.return_value = (
            mock_ui_delegate_interface
        )

        if use_env_var_for_config_file:
            UIDelegateFactory.defaultUIDelegateForInterface(
                mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
            )
        else:
            UIDelegateFactory.defaultUIDelegateForInterface(
                valid_ui_delegate_config,
                mock_host_interface,
                mock_ui_delegate_implementation_factory,
                mock_logger,
            )

        if use_env_var_for_config_file:
            assert mock_logger.mock.log.call_args_list == [
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    "Retrieved default config file path from 'OPENASSETIO_DEFAULT_CONFIG'",
                ),
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    f"Loading default config at '{valid_ui_delegate_config}'",
                ),
            ]
        else:
            assert mock_logger.mock.log.call_args_list == [
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    f"Loading default config at '{valid_ui_delegate_config}'",
                ),
            ]

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_var_set_to_valid_relative_path_then_path_substituted_settings_are_absolute(
        self,
        use_env_var_for_config_file,
        relative_test_ui_delegate_config,
        resources_dir,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_ui_delegate_interface,
    ):
        expected_path = f"{resources_dir}/my/🐈/{resources_dir}"

        mock_ui_delegate_interface = create_mock_ui_delegate_interface()

        def check_initialization(settings, _):
            assert settings["a_config_path_twice"] == expected_path
            return mock.DEFAULT

        mock_ui_delegate_interface.mock.initialize.side_effect = check_initialization

        mock_ui_delegate_implementation_factory.mock.instantiate.return_value = (
            mock_ui_delegate_interface
        )

        if use_env_var_for_config_file:
            UIDelegateFactory.defaultUIDelegateForInterface(
                mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
            )
        else:
            UIDelegateFactory.defaultUIDelegateForInterface(
                relative_test_ui_delegate_config,
                mock_host_interface,
                mock_ui_delegate_implementation_factory,
                mock_logger,
            )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_var_set_to_non_canonical_path_then_path_substituted_settings_are_canonical(
        self,
        use_env_var_for_config_file,
        non_canonical_test_ui_delegate_config,
        resources_dir,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_ui_delegate_interface,
    ):
        expected_path = f"{resources_dir}/my/🐈/{resources_dir}"

        mock_ui_delegate_interface = create_mock_ui_delegate_interface()

        def check_initialization(settings, _):
            assert settings["a_config_path_twice"] == expected_path
            return mock.DEFAULT

        mock_ui_delegate_interface.mock.initialize.side_effect = check_initialization

        mock_ui_delegate_implementation_factory.mock.instantiate.return_value = (
            mock_ui_delegate_interface
        )

        if use_env_var_for_config_file:
            UIDelegateFactory.defaultUIDelegateForInterface(
                mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
            )
        else:
            UIDelegateFactory.defaultUIDelegateForInterface(
                non_canonical_test_ui_delegate_config,
                mock_host_interface,
                mock_ui_delegate_implementation_factory,
                mock_logger,
            )


class Test_UIDelegateFactory_createUIDelegate:
    def test_returns_a_ui_delegate(self, a_ui_delegate_factory):
        ui_delegate = a_ui_delegate_factory.createUIDelegate("a.ui_delegate")
        assert isinstance(ui_delegate, UIDelegate)

    def test_ui_delegate_is_properly_configured(
        self,
        assert_expected_ui_delegate,
        a_ui_delegate_factory,
        mock_ui_delegate_implementation_factory,
    ):
        # setup

        expected_identifier = "a.ui_delegate"

        # action

        ui_delegate = a_ui_delegate_factory.createUIDelegate(expected_identifier)

        # confirm

        assert isinstance(ui_delegate, UIDelegate)
        mock_ui_delegate_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_identifier
        )
        assert_expected_ui_delegate(ui_delegate)


class Test_UIDelegateFactory_createUIDelegateForInterface:
    def test_returns_a_ui_delegate(
        self, mock_ui_delegate_implementation_factory, mock_host_interface, mock_logger
    ):
        ui_delegate = UIDelegateFactory.createUIDelegateForInterface(
            "a.ui_delegate",
            mock_host_interface,
            mock_ui_delegate_implementation_factory,
            mock_logger,
        )

        assert isinstance(ui_delegate, UIDelegate)

    def test_ui_delegate_is_properly_configured(
        self,
        assert_expected_ui_delegate,
        mock_ui_delegate_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        # setup

        expected_identifier = "a.ui_delegate"

        # action

        ui_delegate = UIDelegateFactory.createUIDelegateForInterface(
            expected_identifier,
            mock_host_interface,
            mock_ui_delegate_implementation_factory,
            mock_logger,
        )

        # confirm

        mock_ui_delegate_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_identifier
        )
        assert_expected_ui_delegate(ui_delegate)


@pytest.fixture
def assert_expected_ui_delegate(mock_host_interface, mock_ui_delegate_interface):
    # Assert the expected UI delegate is constructed and is given the
    # expected host session in method calls (`settings()` abused
    # here for this purpose).
    def assert_for_ui_delegate(ui_delegate):
        expected_host_identifier = "a.host"
        expected_settings = {"some": "settings"}

        mock_host_interface.mock.identifier.return_value = expected_host_identifier

        def assert_expected_host(hostSession):
            assert hostSession.host().identifier() == expected_host_identifier
            return mock.DEFAULT

        mock_ui_delegate_interface.mock.settings.side_effect = assert_expected_host
        mock_ui_delegate_interface.mock.settings.return_value = expected_settings

        assert ui_delegate.settings() == expected_settings

    return assert_for_ui_delegate


@pytest.fixture
def a_ui_delegate_factory(
    mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
):
    return UIDelegateFactory(
        mock_host_interface, mock_ui_delegate_implementation_factory, mock_logger
    )


@pytest.fixture
def mock_ui_delegate_implementation_factory(mock_logger, mock_ui_delegate_interface):
    factory = MockUIDelegateImplementationFactory(mock_logger)
    factory.mock.instantiate.return_value = mock_ui_delegate_interface
    return factory


@pytest.fixture
def resources_dir():
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "resources")


@pytest.fixture()
def valid_ui_delegate_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = os.path.join(resources_dir, "default_ui_delegate.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


@pytest.fixture
def relative_test_ui_delegate_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = pathlib.Path(resources_dir, "default_ui_delegate.toml")

    # Ensure cwd is on the same drive letter in Windows.
    cwd = toml_path.parent.parent
    monkeypatch.chdir(cwd)

    toml_relative_path = os.path.relpath(toml_path, cwd)
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_relative_path)
    return toml_relative_path


@pytest.fixture
def non_canonical_test_ui_delegate_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    parts = pathlib.Path(resources_dir).parts
    # (/, path, to, config.toml) -> (/, path, .., path, to, config.toml)
    parts = parts[0:2] + ("..",) + parts[1:]
    toml_path = os.path.join(*parts, "default_ui_delegate.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


@pytest.fixture
def non_existent_ui_delegate_config(monkeypatch, use_env_var_for_config_file):
    toml_path = "i/do/not/exist"
    if use_env_var_for_config_file:
        monkeypatch.setenv(UIDelegateFactory.kDefaultUIDelegateConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture
def directory_ui_delegate_config(
    monkeypatch, use_env_var_for_config_file, valid_ui_delegate_config
):
    toml_path = os.path.dirname(valid_ui_delegate_config)
    if use_env_var_for_config_file:
        monkeypatch.setenv(UIDelegateFactory.kDefaultUIDelegateConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture
def invalid_ui_delegate_config(monkeypatch, use_env_var_for_config_file):
    toml_path = __file__
    if use_env_var_for_config_file:
        monkeypatch.setenv(UIDelegateFactory.kDefaultUIDelegateConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture
def config_with_invalid_property(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = os.path.join(resources_dir, "unsupported_value_type.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


class MockUIDelegateImplementationFactory(UIDelegateImplementationFactoryInterface):
    """
    `UIDelegateImplementationFactoryInterface` that forwards calls to an
    internal mock.
    @see mock_ui_delegate_implementation_factory
    """

    def __init__(self, logger):
        UIDelegateImplementationFactoryInterface.__init__(self, logger)
        self.mock = mock.create_autospec(
            UIDelegateImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
