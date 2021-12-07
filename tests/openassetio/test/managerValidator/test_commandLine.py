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
Unit tests for the commandLine module of the manager test harness.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-arguments,too-few-public-methods

import tempfile
import textwrap
import types
import unittest
from unittest import mock
from unittest.mock import Mock

import pytest

from openassetio.test.managerValidator import commandLine, validatorHarness


class Test_execute:
    def test_constructs_dependencies_and_runs_tests(
            self, mock_parser, mock_module, mock_host_interface, mock_session,
            mock_manager_factory, mock_logger, mock_harness_factory, mock_case_loader,
            mock_harness):
        # setup

        argv = Mock()
        parsed = mock_parser.parse.return_value

        # action

        result = commandLine.execute(
            argv, mock_module, parser=mock_parser, harnessFactory=mock_harness_factory)

        # confirm

        mock_parser.parse.assert_called_once_with(argv)
        mock_harness_factory.createHostInterface.assert_called_once_with()
        mock_harness_factory.createLogger.assert_called_once_with()
        mock_harness_factory.createManagerFactory.assert_called_once_with(mock_logger)
        mock_harness_factory.createSessionWithManager.assert_called_once_with(
            parsed.fixtures["identifier"], mock_host_interface, mock_logger, mock_manager_factory)
        mock_harness_factory.createLoader.assert_called_once_with(parsed.fixtures, mock_session)
        mock_harness_factory.createHarness.assert_called_once_with(unittest.main, mock_case_loader)
        mock_harness.executeTests.assert_called_once_with(parsed.extraArgs, mock_module)
        assert result is mock_harness.executeTests.return_value


class Test_Parser_parse:
    def test_loads_fixtures_and_returns_with_extra_args(self, mock_fixture_loader):
        parser = commandLine.Parser(mock_fixture_loader)

        parsed = parser.parse([
            "managerValidator", "--fixtures", "/some/fixtures.json", "-v", "extra", "arg"])

        mock_fixture_loader.load.assert_called_once_with("/some/fixtures.json")
        assert parsed.fixtures is mock_fixture_loader.load.return_value
        assert parsed.extraArgs == ["-v", "extra", "arg"]


class Test_FixtureLoader_load:
    def test_retrieves_dict_from_python_file(self, a_fixture_dict, a_fixture_file):
        fixture_loader = commandLine.PyFixtureLoader()

        actual_dict = fixture_loader.load(a_fixture_file)

        assert a_fixture_dict == actual_dict


@pytest.fixture
def mock_parser():
    parser = mock.create_autospec(commandLine.Parser)
    parsed = mock.create_autospec(commandLine.ParsedArgs)
    parser.parse.return_value = parsed
    return parser


@pytest.fixture
def mock_module():
    return mock.create_autospec(types.ModuleType)


@pytest.fixture
def mock_harness_factory(
        mock_harness, mock_case_loader, mock_host_interface, mock_session, mock_manager_factory,
        mock_logger):
    factory = mock.create_autospec(
        validatorHarness.ValidatorHarnessFactory, instance=True, spec_set=True)
    factory.createHarness.return_value = mock_harness
    factory.createLoader.return_value = mock_case_loader
    factory.createHostInterface.return_value = mock_host_interface
    factory.createSessionWithManager.return_value = mock_session
    factory.createManagerFactory.return_value = mock_manager_factory
    factory.createLogger.return_value = mock_logger
    return factory


@pytest.fixture
def mock_harness():
    return mock.create_autospec(validatorHarness.ValidatorHarness, instance=True, spec_set=True)


@pytest.fixture
def mock_case_loader():
    return mock.create_autospec(validatorHarness.ValidatorTestLoader, instance=True, spec_set=True)


@pytest.fixture
def mock_fixture_loader():
    return mock.create_autospec(commandLine.PyFixtureLoader, instance=True, spec_set=True)


@pytest.fixture
def a_fixture_file(a_fixture_dict):
    with tempfile.NamedTemporaryFile(suffix=".py") as fixture_file:
        fixture_file.write(textwrap.dedent(f"""
            fixtures = {a_fixture_dict}
        """).encode())

        fixture_file.flush()

        yield fixture_file.name
