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
Unit tests for the validatorHarness module of the manager test harness.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-arguments,too-few-public-methods
# pylint: disable=protected-access

import unittest
from unittest import mock
from unittest.mock import Mock, call

import pytest

from openassetio import logging, pluginSystem, hostAPI
from openassetio.test.managerValidator import validatorHarness


class Test_ValidatorHarnessFactory_createHarness:
    def test_constructs_harness(self, monkeypatch, mock_runner, mock_test_loader):
        StubHarness = mock.create_autospec(
            validatorHarness.ValidatorHarness, instance=False, spec_set=True)
        monkeypatch.setattr(validatorHarness, "ValidatorHarness", StubHarness)

        harness = validatorHarness.ValidatorHarnessFactory().createHarness(
            mock_runner, mock_test_loader)

        assert harness is StubHarness.return_value


class Test_ValidatorHarnessFactory_createLoader:
    def test_constructs_loader(self, monkeypatch, a_fixture_dict, mock_session):
        StubLoader = mock.create_autospec(
            validatorHarness.ValidatorTestLoader, instance=False, spec_set=True)
        monkeypatch.setattr(validatorHarness, "ValidatorTestLoader", StubLoader)

        loader = validatorHarness.ValidatorHarnessFactory().createLoader(
            a_fixture_dict, mock_session)

        assert loader is StubLoader.return_value


class Test_ValidatorHarnessFactory_createHostInterface:
    def test_constructs_interface(self, monkeypatch):
        StubHostInterface = mock.create_autospec(
            validatorHarness.ValidatorHarnessHostInterface, instance=False, spec_set=True)
        monkeypatch.setattr(validatorHarness, "ValidatorHarnessHostInterface", StubHostInterface)

        interface = validatorHarness.ValidatorHarnessFactory().createHostInterface()

        assert interface is StubHostInterface.return_value


class Test_ValidatorHarnessFactory_createSession:
    def test_constructs_session(self, monkeypatch, mock_host_interface, mock_logger):
        manager_factory = mock.create_autospec(hostAPI.ManagerFactoryInterface)
        StubSession = mock.create_autospec(hostAPI.Session, instance=False, spec_set=True)
        monkeypatch.setattr(hostAPI, "Session", StubSession)

        session = validatorHarness.ValidatorHarnessFactory().createSessionWithManager(
            "org.some.id", mock_host_interface, mock_logger, manager_factory)

        StubSession.assert_called_once_with(mock_host_interface, mock_logger, manager_factory)
        session.useManager.assert_called_once_with("org.some.id")  # pylint: disable=no-member
        assert session is StubSession.return_value


class Test_ValidatorHarnessFactory_createManagerFactory:
    def test_constructs_factory(self, monkeypatch, mock_logger):
        StubManagerFactory = mock.create_autospec(
            pluginSystem.PluginSystemManagerFactory, instance=False, spec_set=True)
        monkeypatch.setattr(pluginSystem, "PluginSystemManagerFactory", StubManagerFactory)

        manager_factory = validatorHarness.ValidatorHarnessFactory().createManagerFactory(
            mock_logger)

        StubManagerFactory.assert_called_once_with(mock_logger)
        assert manager_factory is StubManagerFactory.return_value


class Test_ValidatorHarnessFactory_createLogger:
    def test_constructs_logger(self, monkeypatch):
        StubFilter = mock.create_autospec(logging.SeverityFilter, instance=False, spec_set=True)
        monkeypatch.setattr(logging, "SeverityFilter", StubFilter)
        StubLogger = mock.create_autospec(logging.ConsoleLogger, instance=False, spec_set=True)
        monkeypatch.setattr(logging, "ConsoleLogger", StubLogger)

        manager_factory = validatorHarness.ValidatorHarnessFactory().createLogger()

        StubFilter.assert_called_once_with(StubLogger.return_value)
        assert manager_factory is StubFilter.return_value


class Test_Harness_executeTests:
    def test_executes_runner_and_returns_runner_result(self, mock_runner, mock_test_loader):
        module = Mock()
        harness = validatorHarness.ValidatorHarness(mock_runner, mock_test_loader)

        result = harness.executeTests(["some", "args"], module)

        mock_runner.assert_called_once_with(
            testLoader=mock_test_loader, argv=["managerValidator", "some", "args"],
            module=module, exit=False)
        assert result is mock_runner.return_value.result.wasSuccessful.return_value


class Test_Loader_loadTestsFromTestCase:
    def test_when_class_of_cases_has_no_fixtures_then_initialises_test_cases_with_no_fixtures(
            self, a_fixture_dict, mock_session, mock_test_case_class, mock_test_case_one,
            mock_test_case_two):
        # setup

        loader = validatorHarness.ValidatorTestLoader(a_fixture_dict, mock_session)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(None, mock_session, "test_one"),
            call(None, mock_session, "test_two")])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_cases_have_fixtures_then_initialises_test_cases_with_fixtures(
            self, a_fixture_dict, mock_session, mock_test_case_class, mock_test_case_one,
            mock_test_case_two):
        # setup

        # Include fixtures for both test cases
        case_one_fixtures = Mock()
        case_two_fixtures = Mock()
        a_fixture_dict["Test_MockTest"] = {
            "test_one": case_one_fixtures,
            "test_two": case_two_fixtures
        }
        loader = validatorHarness.ValidatorTestLoader(a_fixture_dict, mock_session)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(case_one_fixtures, mock_session, "test_one"),
            call(case_two_fixtures, mock_session, "test_two")])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_case_has_no_fixtures_then_initialises_test_case_with_no_fixtures(
            self, a_fixture_dict, mock_session, mock_test_case_class, mock_test_case_one,
            mock_test_case_two):
        # setup

        # Only include fixtures for one test case
        case_two_fixtures = Mock()
        a_fixture_dict["Test_MockTest"] = {
            "test_two": case_two_fixtures
        }
        loader = validatorHarness.ValidatorTestLoader(a_fixture_dict, mock_session)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(None, mock_session, "test_one"),
            call(case_two_fixtures, mock_session, "test_two")])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}


class Test_ValidatorHostInterface_identifier:
    def test_returns_expected_id(self):
        interface = validatorHarness.ValidatorHarnessHostInterface()
        assert interface.identifier() == "org.openassetio.test.managerValidator"


class Test_ValidatorHostInterface_displayName:
    def test_returns_expected_name(self):
        interface = validatorHarness.ValidatorHarnessHostInterface()
        assert interface.displayName() == "OpenAssetIO Manager Validator"


class Test_FixtureAugmentedTestCase_init:
    def test_has_fixtures_session_and_manager(
            self, mock_test_case, a_fixture_dict, mock_session, mock_manager):
        assert mock_test_case._fixtures is a_fixture_dict
        assert mock_test_case._session is mock_session
        assert mock_test_case._manager is mock_manager


class Test_FixtureAugmentedTestCase_assertIsStringKeyPrimitiveValueDict:
    def test_when_not_dict_then_fails(self, mock_test_case):
        with pytest.raises(AssertionError):
            mock_test_case.assertIsStringKeyPrimitiveValueDict("something")

    def test_when_dict_empty_then_passes(self, mock_test_case):
        mock_test_case.assertIsStringKeyPrimitiveValueDict({})

    def test_when_dict_ok_then_passes(self, mock_test_case):
        mock_test_case.assertIsStringKeyPrimitiveValueDict({
            "k1": 1, "k2": 1.1, "k3": "v", "k4": True
        })

    def test_when_dict_has_non_string_key_then_fails(self, mock_test_case):
        with pytest.raises(AssertionError):
            mock_test_case.assertIsStringKeyPrimitiveValueDict({
                1: 1
            })

    def test_when_dict_has_nested_dict_then_fails(self, mock_test_case):
        with pytest.raises(AssertionError):
            mock_test_case.assertIsStringKeyPrimitiveValueDict({
                "k": {}
            })

    def test_when_dict_has_None_then_fails(self, mock_test_case):
        with pytest.raises(AssertionError):
            mock_test_case.assertIsStringKeyPrimitiveValueDict({
                "k": None
            })

    def test_when_dict_has_object_then_fails(self, mock_test_case):
        with pytest.raises(AssertionError):
            mock_test_case.assertIsStringKeyPrimitiveValueDict({
                "k": object()
            })


@pytest.fixture
def mock_runner():
    result = mock.create_autospec(unittest.result.TestResult, instance=True, spec_set=True)
    instance = mock.create_autospec(unittest.main, instance=True, result=result)
    cls = mock.create_autospec(
        unittest.main, instance=False, spec_set=True, return_value=instance)
    return cls


@pytest.fixture
def mock_test_loader():
    return mock.create_autospec(validatorHarness.ValidatorTestLoader, instance=True, spec_set=True)


@pytest.fixture
def mock_test_case(a_fixture_dict, mock_session):
    return validatorHarness.FixtureAugmentedTestCase(a_fixture_dict, mock_session)


@pytest.fixture
def mock_test_case_class(mock_test_case_one, mock_test_case_two):
    # Construct a mock TestCase class with two test methods.
    # In unittest each method runs under a new instance of the
    # TestCase class.
    test_case_class = mock.create_autospec(
        validatorHarness.FixtureAugmentedTestCase, instance=False,
        test_one=Mock(), test_two=Mock(),
        # Note that __qualname__ is required simply to prevent
        # exceptions from `getTestCaseNames`.
        __qualname__="something",
        __name__="Test_MockTest"
    )
    test_case_class.side_effect = [mock_test_case_one, mock_test_case_two]
    return test_case_class


@pytest.fixture
def mock_test_case_one():
    return mock.create_autospec(
        validatorHarness.FixtureAugmentedTestCase, instance=True, spec_set=True)


@pytest.fixture
def mock_test_case_two():
    return mock.create_autospec(
        validatorHarness.FixtureAugmentedTestCase, instance=True, spec_set=True)
