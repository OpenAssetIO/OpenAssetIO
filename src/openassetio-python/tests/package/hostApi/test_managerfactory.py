#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.hostApi.ManagerFactory class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import os
import pathlib
from unittest import mock

import pytest

from openassetio import errors
from openassetio.hostApi import ManagerFactory, Manager, ManagerImplementationFactoryInterface
from openassetio.log import LoggerInterface


class Test_ManagerFactory_ManagerDetail_equality:
    def test_when_other_is_equal_then_compares_equal(self):
        managerDetails = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )
        otherManagerDetail = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )

        assert managerDetails == otherManagerDetail

    @pytest.mark.parametrize(
        "otherManagerDetail",
        [
            ManagerFactory.ManagerDetail(identifier="z", displayName="b", info={"c": "d"}),
            ManagerFactory.ManagerDetail(identifier="a", displayName="z", info={"c": "d"}),
            ManagerFactory.ManagerDetail(identifier="a", displayName="b", info={"c": "z"}),
        ],
    )
    def test_when_other_has_unequal_field_then_object_compares_unequal(self, otherManagerDetail):
        managerDetails = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"}
        )

        assert managerDetails != otherManagerDetail


class Test_ManagerFactory_identifiers:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_manager_implementation_factory, a_manager_factory
    ):
        expected = ["first.identifier", "second.identifier"]
        mock_manager_implementation_factory.mock.identifiers.return_value = expected

        actual = a_manager_factory.identifiers()

        assert actual == expected


class Test_ManagerFactory_availableManagers:
    def test_when_no_implemetations_then_reports_no_implemetation_detais(
        self, mock_manager_implementation_factory, a_manager_factory
    ):
        mock_manager_implementation_factory.mock.identifiers.return_value = []
        mock_manager_implementation_factory.mock.instantiate.side_effect = []

        expected = {}

        # action

        actual = a_manager_factory.availableManagers()

        # confirm

        assert actual == expected

    def test_when_has_implementations_then_reports_implementation_details(
        self, create_mock_manager_interface, mock_manager_implementation_factory, a_manager_factory
    ):
        # setup

        identifiers = ["first.identifier", "second.identifier"]
        mock_manager_implementation_factory.mock.identifiers.return_value = identifiers

        first_manager_interface = create_mock_manager_interface()
        second_manager_interface = create_mock_manager_interface()
        first_manager_interface.mock.identifier.return_value = "first.identifier"
        second_manager_interface.mock.identifier.return_value = "second.identifier"
        first_manager_interface.mock.displayName.return_value = "First"
        second_manager_interface.mock.displayName.return_value = "Second"
        first_manager_interface.mock.info.return_value = {"first": "info"}
        second_manager_interface.mock.info.return_value = {"second": "info"}

        mock_manager_implementation_factory.mock.instantiate.side_effect = [
            first_manager_interface,
            second_manager_interface,
        ]

        expected = {
            "first.identifier": ManagerFactory.ManagerDetail(
                identifier="first.identifier", displayName="First", info={"first": "info"}
            ),
            "second.identifier": ManagerFactory.ManagerDetail(
                identifier="second.identifier", displayName="Second", info={"second": "info"}
            ),
        }

        # action

        actual = a_manager_factory.availableManagers()

        # confirm

        assert actual == expected


class Test_ManagerFactory_kDefaultManagerConfigEnvVarName:
    def test_has_expected_value(self):
        assert ManagerFactory.kDefaultManagerConfigEnvVarName == "OPENASSETIO_DEFAULT_CONFIG"


class Test_ManagerFactory_defaultManagerForInterface:
    def test_when_var_not_set_then_returns_none(
        self, mock_manager_implementation_factory, mock_host_interface, mock_logger
    ):
        assert (
            ManagerFactory.defaultManagerForInterface(
                mock_host_interface, mock_manager_implementation_factory, mock_logger
            )
            is None
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_non_existent_path_then_InputValidationException_raised(
        self,
        use_env_var_for_config_file,
        non_existent_manager_config,  # pylint: disable=unused-argument
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(errors.InputValidationException) as exc:
            if use_env_var_for_config_file:
                ManagerFactory.defaultManagerForInterface(
                    mock_host_interface, mock_manager_implementation_factory, mock_logger
                )
            else:
                ManagerFactory.defaultManagerForInterface(
                    non_existent_manager_config,
                    mock_host_interface,
                    mock_manager_implementation_factory,
                    mock_logger,
                )

        assert (
            str(exc.value)
            == "Could not load default manager config from 'i/do/not/exist', file does not exist."
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_directory_then_InputValidationException_raised(
        self,
        use_env_var_for_config_file,
        directory_manager_config,  # pylint: disable=unused-argument
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(errors.InputValidationException) as exc:
            if use_env_var_for_config_file:
                ManagerFactory.defaultManagerForInterface(
                    mock_host_interface,
                    mock_manager_implementation_factory,
                    mock_logger,
                )
            else:
                ManagerFactory.defaultManagerForInterface(
                    directory_manager_config,
                    mock_host_interface,
                    mock_manager_implementation_factory,
                    mock_logger,
                )

        assert (
            str(exc.value)
            == f"Could not load default manager config from '{directory_manager_config}', "
            "must be a TOML file not a directory."
        )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_invalid_format_then_ConfigurationException_raised(
        self,
        use_env_var_for_config_file,
        invalid_manager_config,
        mock_manager_implementation_factory,
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
                ManagerFactory.defaultManagerForInterface(
                    mock_host_interface, mock_manager_implementation_factory, mock_logger
                )
            else:
                ManagerFactory.defaultManagerForInterface(
                    invalid_manager_config,
                    mock_host_interface,
                    mock_manager_implementation_factory,
                    mock_logger,
                )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_invalid_property_type_then_ConfigurationException_raised(
        self,
        use_env_var_for_config_file,
        config_with_invalid_property,
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        with pytest.raises(
            errors.ConfigurationException, match="Unsupported value type for 'a_dict'."
        ):
            if use_env_var_for_config_file:
                ManagerFactory.defaultManagerForInterface(
                    mock_host_interface, mock_manager_implementation_factory, mock_logger
                )
            else:
                ManagerFactory.defaultManagerForInterface(
                    config_with_invalid_property,
                    mock_host_interface,
                    mock_manager_implementation_factory,
                    mock_logger,
                )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_valid_path_then_expected_manager_returned_with_expected_settings(
        self,
        use_env_var_for_config_file,
        valid_manager_config,  # pylint: disable=unused-argument
        resources_dir,
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_manager_interface,
    ):
        expected_host_identifier = "a.host"
        mock_host_interface.mock.identifier.return_value = expected_host_identifier

        expected_manager_identifier = "identifier.from.toml.file"

        expected_settings = {
            "a_string": "Hello 🐈",
            "a_float": 3.141579,
            "a_bool": False,
            "a_int": 42,
            "a_config_path_twice": f"{resources_dir}/my/🐈/{resources_dir}",
        }

        mock_manager_interface = create_mock_manager_interface()
        mock_manager_interface.mock.identifier.return_value = expected_manager_identifier

        # Use a side-effect to check host_session as this is constructed
        # privately by the factory.
        def check_initialization(settings, host_session):
            assert settings == expected_settings
            assert host_session.host().identifier() == expected_host_identifier
            return mock.DEFAULT

        mock_manager_interface.mock.initialize.side_effect = check_initialization

        mock_manager_implementation_factory.mock.instantiate.return_value = mock_manager_interface

        if use_env_var_for_config_file:
            manager = ManagerFactory.defaultManagerForInterface(
                mock_host_interface, mock_manager_implementation_factory, mock_logger
            )
        else:
            manager = ManagerFactory.defaultManagerForInterface(
                valid_manager_config,
                mock_host_interface,
                mock_manager_implementation_factory,
                mock_logger,
            )

        assert manager.identifier() == expected_manager_identifier
        mock_manager_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_manager_identifier
        )
        mock_manager_interface.mock.initialize.assert_called_once()

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_valid_path_then_expected_log_messages_printed(
        self,
        use_env_var_for_config_file,
        valid_manager_config,  # pylint: disable=unused-argument
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_manager_interface,
    ):
        mock_manager_interface = create_mock_manager_interface()
        mock_manager_implementation_factory.mock.instantiate.return_value = mock_manager_interface

        if use_env_var_for_config_file:
            ManagerFactory.defaultManagerForInterface(
                mock_host_interface, mock_manager_implementation_factory, mock_logger
            )
        else:
            ManagerFactory.defaultManagerForInterface(
                valid_manager_config,
                mock_host_interface,
                mock_manager_implementation_factory,
                mock_logger,
            )

        if use_env_var_for_config_file:
            assert mock_logger.mock.log.call_args_list == [
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    "Retrieved default manager config file path from 'OPENASSETIO_DEFAULT_CONFIG'",
                ),
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    f"Loading default manager config at '{valid_manager_config}'",
                ),
            ]
        else:
            assert mock_logger.mock.log.call_args_list == [
                mock.call(
                    LoggerInterface.Severity.kDebug,
                    f"Loading default manager config at '{valid_manager_config}'",
                ),
            ]

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_var_set_to_valid_relative_path_then_path_substituted_settings_are_absolute(
        self,
        use_env_var_for_config_file,
        relative_test_manager_config,
        resources_dir,
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_manager_interface,
    ):
        expected_path = f"{resources_dir}/my/🐈/{resources_dir}"

        mock_manager_interface = create_mock_manager_interface()

        def check_initialization(settings, _):
            assert settings["a_config_path_twice"] == expected_path
            return mock.DEFAULT

        mock_manager_interface.mock.initialize.side_effect = check_initialization

        mock_manager_implementation_factory.mock.instantiate.return_value = mock_manager_interface

        if use_env_var_for_config_file:
            ManagerFactory.defaultManagerForInterface(
                mock_host_interface, mock_manager_implementation_factory, mock_logger
            )
        else:
            ManagerFactory.defaultManagerForInterface(
                relative_test_manager_config,
                mock_host_interface,
                mock_manager_implementation_factory,
                mock_logger,
            )

    @pytest.mark.parametrize("use_env_var_for_config_file", [True, False])
    def test_when_var_set_to_non_canonical_path_then_path_substituted_settings_are_canonical(
        self,
        use_env_var_for_config_file,
        non_canonical_test_manager_config,
        resources_dir,
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
        create_mock_manager_interface,
    ):
        expected_path = f"{resources_dir}/my/🐈/{resources_dir}"

        mock_manager_interface = create_mock_manager_interface()

        def check_initialization(settings, _):
            assert settings["a_config_path_twice"] == expected_path
            return mock.DEFAULT

        mock_manager_interface.mock.initialize.side_effect = check_initialization

        mock_manager_implementation_factory.mock.instantiate.return_value = mock_manager_interface

        if use_env_var_for_config_file:
            ManagerFactory.defaultManagerForInterface(
                mock_host_interface, mock_manager_implementation_factory, mock_logger
            )
        else:
            ManagerFactory.defaultManagerForInterface(
                non_canonical_test_manager_config,
                mock_host_interface,
                mock_manager_implementation_factory,
                mock_logger,
            )


class Test_ManagerFactory_createManager:
    def test_returns_a_manager(self, a_manager_factory):
        manager = a_manager_factory.createManager("a.manager")
        assert isinstance(manager, Manager)

    def test_manager_is_properly_configured(
        self, assert_expected_manager, a_manager_factory, mock_manager_implementation_factory
    ):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = a_manager_factory.createManager(expected_identifier)

        # confirm

        assert isinstance(manager, Manager)
        mock_manager_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_identifier
        )
        assert_expected_manager(manager)


class Test_ManagerFactory_createManagerForInterface:
    def test_returns_a_manager(
        self, mock_manager_implementation_factory, mock_host_interface, mock_logger
    ):
        manager = ManagerFactory.createManagerForInterface(
            "a.manager", mock_host_interface, mock_manager_implementation_factory, mock_logger
        )

        assert isinstance(manager, Manager)

    def test_manager_is_properly_configured(
        self,
        assert_expected_manager,
        mock_manager_implementation_factory,
        mock_host_interface,
        mock_logger,
    ):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = ManagerFactory.createManagerForInterface(
            expected_identifier,
            mock_host_interface,
            mock_manager_implementation_factory,
            mock_logger,
        )

        # confirm

        mock_manager_implementation_factory.mock.instantiate.assert_called_once_with(
            expected_identifier
        )
        assert_expected_manager(manager)


@pytest.fixture
def assert_expected_manager(mock_host_interface, mock_manager_interface):
    # Assert the expected manager is constructed and is given the
    # expected host session in method calls (`settings()` abused
    # here for this purpose).
    def assert_for_manager(manager):
        expected_host_identifier = "a.host"
        expected_settings = {"some": "settings"}

        mock_host_interface.mock.identifier.return_value = expected_host_identifier

        def assert_expected_host(hostSession):
            assert hostSession.host().identifier() == expected_host_identifier
            return mock.DEFAULT

        mock_manager_interface.mock.settings.side_effect = assert_expected_host
        mock_manager_interface.mock.settings.return_value = expected_settings

        assert manager.settings() == expected_settings

    return assert_for_manager


@pytest.fixture
def a_manager_factory(mock_host_interface, mock_manager_implementation_factory, mock_logger):
    return ManagerFactory(mock_host_interface, mock_manager_implementation_factory, mock_logger)


@pytest.fixture
def mock_manager_implementation_factory(mock_logger, mock_manager_interface):
    factory = MockManagerImplementationFactory(mock_logger)
    factory.mock.instantiate.return_value = mock_manager_interface
    return factory


@pytest.fixture
def resources_dir():
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "resources")


@pytest.fixture()
def valid_manager_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = os.path.join(resources_dir, "default_manager.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


@pytest.fixture
def relative_test_manager_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = pathlib.Path(resources_dir, "default_manager.toml")

    # Ensure cwd is on the same drive letter in Windows.
    cwd = toml_path.parent.parent
    monkeypatch.chdir(cwd)

    toml_relative_path = os.path.relpath(toml_path, cwd)
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_relative_path)
    return toml_relative_path


@pytest.fixture
def non_canonical_test_manager_config(resources_dir, monkeypatch, use_env_var_for_config_file):
    parts = pathlib.Path(resources_dir).parts
    # (/, path, to, config.toml) -> (/, path, .., path, to, config.toml)
    parts = parts[0:2] + ("..",) + parts[1:]
    toml_path = os.path.join(*parts, "default_manager.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


@pytest.fixture()
def non_existent_manager_config(monkeypatch, use_env_var_for_config_file):
    toml_path = "i/do/not/exist"
    if use_env_var_for_config_file:
        monkeypatch.setenv(ManagerFactory.kDefaultManagerConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture()
def directory_manager_config(monkeypatch, use_env_var_for_config_file, valid_manager_config):
    toml_path = os.path.dirname(valid_manager_config)
    if use_env_var_for_config_file:
        monkeypatch.setenv(ManagerFactory.kDefaultManagerConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture()
def invalid_manager_config(monkeypatch, use_env_var_for_config_file):
    toml_path = __file__
    if use_env_var_for_config_file:
        monkeypatch.setenv(ManagerFactory.kDefaultManagerConfigEnvVarName, toml_path)
    return toml_path


@pytest.fixture
def config_with_invalid_property(resources_dir, monkeypatch, use_env_var_for_config_file):
    toml_path = os.path.join(resources_dir, "unsupported_value_type.toml")
    if use_env_var_for_config_file:
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", toml_path)
    return toml_path


class MockManagerImplementationFactory(ManagerImplementationFactoryInterface):
    """
    `ManagerImplementationFactoryInterface` that forwards calls to an
    internal mock.
    @see mock_manager_implementation_factory
    """

    def __init__(self, logger):
        ManagerImplementationFactoryInterface.__init__(self, logger)
        self.mock = mock.create_autospec(
            ManagerImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
