#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
Test cases that are run as part of the unit tests for `executeSuite`.
They assert the expected public API of `FixtureAugmentedTestCase`, and
that the harness implementation supplies the correct state to each test.
"""

# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring,missing-function-docstring

from openassetio.hostAPI import Manager, Session
from openassetio.test.manager.specifications import ManagerTestHarnessLocale
from openassetio.test.manager.harness import FixtureAugmentedTestCase


__all__ = []


class Test_executeSuite_session(FixtureAugmentedTestCase):

    def test_when_called_then_session_is_set(self):
        self.assertIsInstance(self._session, Session)

    def test_when_called_then_session_has_expected_host(self):
        self.assertEqual(
            self._session.host().identifier(),
            "org.openassetio.test.manager.harness"
        )


class Test_executeSuite_manager(FixtureAugmentedTestCase):

    def test_when_called_then_manager_is_set(self):
        self.assertIsInstance(self._manager, Manager)

    def test_when_called_then_manager_is_that_of_the_session(self):
        self.assertIs(self._manager, self._session.currentManager())

    def test_when_called_then_manager_is_the_expected_manager(self):
        self.assertEqual(
            self._manager.identifier(),
            "org.openassetio.test.manager.stubManager"
        )


class Test_executeSuite_fixtures(FixtureAugmentedTestCase):

    def test_when_test_function_is_run_then_fixtures_are_those_for_the_test(self):
        self.assertDictEqual(
            self._fixtures,
            {
                "aUniqueValue": 5
            }
        )


class Test_executeSuite_locale(FixtureAugmentedTestCase):

    def test_when_test_function_is_run_then_locale_is_set(self):
        self.assertIsInstance(self._locale, ManagerTestHarnessLocale)
        self.assertEqual(
            self._locale.testCase,
            'Test_executeSuite_locale'
            '.test_when_test_function_is_run_then_locale_is_set')

    def test_when_test_function_is_run_then_locale_testCase_is_function_specific(self):
        self.assertEqual(
            self._locale.testCase,
            'Test_executeSuite_locale'
            '.test_when_test_function_is_run_then_locale_testCase_is_function_specific')


# Contrived tests that are expected by the actual test suite.
# They exist so that we can validate they are run and present in
# the process output.

class Test_executeSuite_no_case_fixtures(FixtureAugmentedTestCase):

    def test_with_no_fixture_values(self):
        pass

class Test_executeSuite_with_case_fixtures(FixtureAugmentedTestCase):

    def test_with_no_fixture_values(self):
        pass
