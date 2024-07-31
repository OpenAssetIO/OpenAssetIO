#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-arguments,too-few-public-methods
# pylint: disable=protected-access,unused-argument

from unittest import mock
from unittest.mock import Mock, call

import pytest

from openassetio.test import kTestHarnessTraitId, kCasePropertyKey
from openassetio.test.manager.harness import FixtureAugmentedTestCase
from openassetio.test.manager import _implementation
from openassetio.trait import TraitsData
from openassetio.hostApi import ManagerFactory
from openassetio import pluginSystem
from openassetio import errors


class Test_Loader_loadTestsFromTestCase:
    def test_when_class_of_cases_has_no_fixtures_then_initializes_test_cases_with_no_fixtures(
        self,
        a_fixture_dict,
        mock_manager,
        mock_test_case_class,
        mock_test_case_one,
        mock_test_case_two,
        test_case_one_locale,
        test_case_two_locale,
    ):
        # setup

        manager_create_fn = Mock()
        manager_create_fn.return_value = mock_manager

        loader = _implementation._ValidatorTestLoader(manager_create_fn)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls(
            [
                call({}, mock_manager, test_case_one_locale, "test_one"),
                call({}, mock_manager, test_case_two_locale, "test_two"),
            ],
            # Ignore the checks on the shareManager cls variable
            any_order=True,
        )
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_cases_have_fixtures_then_initializes_test_cases_with_fixtures(
        self,
        a_fixture_dict,
        mock_manager,
        mock_test_case_class,
        mock_test_case_one,
        mock_test_case_two,
        test_case_one_locale,
        test_case_two_locale,
    ):
        # setup

        manager_create_fn = Mock()
        manager_create_fn.return_value = mock_manager

        # Include fixtures for both test cases
        case_one_fixtures = {}
        case_two_fixtures = {}
        a_fixture_dict["Test_MockTest"] = {
            "test_one": case_one_fixtures,
            "test_two": case_two_fixtures,
        }
        loader = _implementation._ValidatorTestLoader(manager_create_fn)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls(
            [
                call(case_one_fixtures, mock_manager, test_case_one_locale, "test_one"),
                call(case_two_fixtures, mock_manager, test_case_two_locale, "test_two"),
            ],
            # Ignore the checks on the shareManager cls variable
            any_order=True,
        )
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_case_has_no_fixtures_then_initializes_test_case_with_no_fixtures(
        self,
        a_fixture_dict,
        mock_manager,
        mock_test_case_class,
        mock_test_case_one,
        mock_test_case_two,
        test_case_one_locale,
        test_case_two_locale,
    ):
        # setup

        manager_create_fn = Mock()
        manager_create_fn.return_value = mock_manager

        # Only include fixtures for one test case
        case_two_fixtures = {}
        a_fixture_dict["Test_MockTest"] = {"test_two": case_two_fixtures}
        loader = _implementation._ValidatorTestLoader(manager_create_fn)
        loader.setFixtures(a_fixture_dict)

        # action

        suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the instances of the TestCase class are given the
        # Host instance in their constructors.
        mock_test_case_class.assert_has_calls(
            [
                call({}, mock_manager, test_case_one_locale, "test_one"),
                call(case_two_fixtures, mock_manager, test_case_two_locale, "test_two"),
            ],
            # Ignore the checks on the shareManager cls variable
            any_order=True,
        )
        assert set(suite._tests) == {mock_test_case_one, mock_test_case_two}

    def test_when_shareManager_false_then_unique_uninitialized_manager_set(
        self,
        a_fixture_dict,
        mock_manager,
        mock_test_case_class,
        mock_test_case_one,
        mock_test_case_two,
        test_case_one_locale,
        test_case_two_locale,
    ):
        # pylint: disable=unused-argument
        # setup

        def create_manager(initialize=True):  # pylint: disable=unused-argument
            return Mock()

        manager_create_fn = Mock(wraps=create_manager)

        loader = _implementation._ValidatorTestLoader(manager_create_fn)
        loader.setFixtures(a_fixture_dict)

        mock_test_case_class.shareManager = False

        # action

        _suite = loader.loadTestsFromTestCase(mock_test_case_class)

        # confirm

        # Assert that the managers are unique, the second arg to each call
        # is the manager for that test case.
        calls = mock_test_case_class.call_args_list
        assert calls[0][0][1] != calls[1][0][1]

        manager_create_fn.assert_has_calls(
            [
                call(initialize=False),
                call(initialize=False),
            ]
        )


class Test_ValidatorHostInterface_identifier:
    def test_returns_expected_id(self):
        interface = _implementation._ValidatorHarnessHostInterface()
        assert interface.identifier() == "org.openassetio.test.manager.harness"


class Test_ValidatorHostInterface_displayName:
    def test_returns_expected_name(self):
        interface = _implementation._ValidatorHarnessHostInterface()
        assert interface.displayName() == "OpenAssetIO Manager Test Harness"


class Test_FixtureAugmentedTestCase_init:
    def test_has_fixtures_and_manager(self, a_test_case, a_fixture_dict, mock_manager, a_locale):
        assert a_test_case._fixtures is a_fixture_dict
        assert a_test_case._manager is mock_manager
        assert a_test_case._locale is a_locale


# Test that the test harness chooses the correct language manager
# implementation factory based on the reported results of scanning the
# system environment
class Test_createHarness:
    def test_cpp_has_priority_over_python(self, mock_manager_factory, mock_hybrid_plugin_system):
        mock_hybrid_plugin_system.return_value.identifiers.return_value = ["an.asset.manager"]

        _implementation.createHarness("an.asset.manager")

        assert isinstance(
            mock_hybrid_plugin_system.call_args_list[0].args[0][0],
            pluginSystem.CppPluginSystemManagerImplementationFactory,
        )
        assert isinstance(
            mock_hybrid_plugin_system.call_args_list[0].args[0][1],
            pluginSystem.PythonPluginSystemManagerImplementationFactory,
        )

    def test_when_identifier_not_found_then_raises(
        self, mock_manager_factory, mock_hybrid_plugin_system
    ):
        mock_hybrid_plugin_system.return_value.identifiers.return_value = ["another.asset.manager"]

        with pytest.raises(
            errors.InputValidationException,
            match="Test Harness: Could not find Python or Cpp plugin with identifier "
            "'an.asset.manager'",
        ):
            _implementation.createHarness("an.asset.manager")

    def test_when_identifier_found_then_creates_interface(
        self, mock_manager_factory, mock_hybrid_plugin_system
    ):
        mock_hybrid_plugin_system.return_value.identifiers.return_value = ["an.asset.manager"]

        _implementation.createHarness("an.asset.manager")

        mock_manager_factory.createManagerForInterface.assert_called_once_with(
            "an.asset.manager", mock.ANY, mock.ANY, mock.ANY
        )


@pytest.fixture
def mock_manager_factory(monkeypatch):
    mocked = mock.create_autospec(ManagerFactory, spec_set=True)
    monkeypatch.setattr(
        _implementation.hostApi,
        "ManagerFactory",
        mocked,
    )
    return mocked


@pytest.fixture
def mock_hybrid_plugin_system(monkeypatch):
    mocked = mock.create_autospec(
        pluginSystem.HybridPluginSystemManagerImplementationFactory, spec_set=True
    )
    monkeypatch.setattr(
        _implementation,
        "HybridPluginSystemManagerImplementationFactory",
        mocked,
    )
    return mocked


@pytest.fixture
def a_test_case(a_fixture_dict, mock_manager, a_locale):
    return FixtureAugmentedTestCase(a_fixture_dict, mock_manager, a_locale)


@pytest.fixture
def mock_test_case_class(mock_test_case_one, mock_test_case_two):
    # Construct a mock TestCase class with two test methods.
    # In unittest each method runs under a new instance of the
    # TestCase class.
    test_case_class = mock.create_autospec(
        FixtureAugmentedTestCase,
        instance=False,
        test_one=Mock(),
        test_two=Mock(),
        # Note that __qualname__ is required simply to prevent
        # exceptions from `getTestCaseNames`.
        __qualname__="something",
        __name__="Test_MockTest",
    )
    test_case_class.side_effect = [mock_test_case_one, mock_test_case_two]
    return test_case_class


@pytest.fixture
def mock_test_case_one():
    return mock.create_autospec(FixtureAugmentedTestCase, instance=True, spec_set=True)


@pytest.fixture
def mock_test_case_two():
    return mock.create_autospec(FixtureAugmentedTestCase, instance=True, spec_set=True)


@pytest.fixture
def test_case_one_locale():
    traitsData = TraitsData({kTestHarnessTraitId})
    traitsData.setTraitProperty(kTestHarnessTraitId, kCasePropertyKey, "Test_MockTest.test_one")
    return traitsData


@pytest.fixture
def test_case_two_locale():
    traitsData = TraitsData({kTestHarnessTraitId})
    traitsData.setTraitProperty(kTestHarnessTraitId, kCasePropertyKey, "Test_MockTest.test_two")
    return traitsData
