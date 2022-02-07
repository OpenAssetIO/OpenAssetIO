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
Unit tests for the _implementation module of the manager test harness.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-arguments,too-few-public-methods
# pylint: disable=protected-access

from unittest import mock
from unittest.mock import Mock, call

import pytest


from openassetio.test.manager.harness import FixtureAugmentedTestCase
from openassetio.test.manager.specifications import ManagerTestHarnessLocale
from openassetio.test.manager._implementation import (
        _ValidatorHarnessHostInterface, _ValidatorTestLoader)


class Test_Loader_loadTestsFromTestCase:

    def test_when_class_of_cases_has_no_fixtures_then_initializes_test_cases_with_no_fixtures(
            self, a_fixture_dict, mock_session, mock_test_case_class, mock_test_case_one,
            mock_test_case_two):
        # setup

        loader = _ValidatorTestLoader(mock_session)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(None, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_one"}), "test_one"),
            call(None, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_two"}), "test_two")
        ])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_cases_have_fixtures_then_initializes_test_cases_with_fixtures(
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
        loader = _ValidatorTestLoader(mock_session)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(case_one_fixtures, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_one"}), "test_one"),
            call(case_two_fixtures, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_two"}), "test_two")])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_case_has_no_fixtures_then_initializes_test_case_with_no_fixtures(
            self, a_fixture_dict, mock_session, mock_test_case_class, mock_test_case_one,
            mock_test_case_two):
        # setup

        # Only include fixtures for one test case
        case_two_fixtures = Mock()
        a_fixture_dict["Test_MockTest"] = {
            "test_two": case_two_fixtures
        }
        loader = _ValidatorTestLoader(mock_session)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls([
            call(None, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_one"}), "test_one"),
            call(case_two_fixtures, mock_session,
                    ManagerTestHarnessLocale({"testCase": "Test_MockTest.test_two"}), "test_two")
        ])
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}


class Test_ValidatorHostInterface_identifier:
    def test_returns_expected_id(self):
        interface = _ValidatorHarnessHostInterface()
        assert interface.identifier() == "org.openassetio.test.manager.harness"


class Test_ValidatorHostInterface_displayName:
    def test_returns_expected_name(self):
        interface = _ValidatorHarnessHostInterface()
        assert interface.displayName() == "OpenAssetIO Manager Test Harness"


class Test_FixtureAugmentedTestCase_init:
    def test_has_fixtures_session_and_manager(
            self, mock_test_case, a_fixture_dict, mock_session, mock_manager, a_locale):
        assert mock_test_case._fixtures is a_fixture_dict
        assert mock_test_case._session is mock_session
        assert mock_test_case._manager is mock_manager
        assert mock_test_case._locale is a_locale


@pytest.fixture
def mock_test_case(a_fixture_dict, mock_session, a_locale):
    return FixtureAugmentedTestCase(a_fixture_dict, mock_session, a_locale)


@pytest.fixture
def mock_test_case_class(mock_test_case_one, mock_test_case_two):
    # Construct a mock TestCase class with two test methods.
    # In unittest each method runs under a new instance of the
    # TestCase class.
    test_case_class = mock.create_autospec(
        FixtureAugmentedTestCase, instance=False,
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
        FixtureAugmentedTestCase, instance=True, spec_set=True)


@pytest.fixture
def mock_test_case_two():
    return mock.create_autospec(
        FixtureAugmentedTestCase, instance=True, spec_set=True)
