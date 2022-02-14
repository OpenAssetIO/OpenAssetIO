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
@namespace openassetio.test.manager.apiComplianceSuite
A manager test harness test case suite that validates that a specific
manager plugin complies to the relevant core OpenAssetIO API contract.

This suite is solely concerned with verifying that a plugin meets the
requirements of the API, and can handle all documented calling patterns.
For example, that when a
@ref openassetio.managerAPI.ManagerInterface.ManagerInterface.managementPolicy
"managementPolicy" query returns a non-ignored state, that there are no
errors calling the other required methods for a managed entity of that
Specification.

The suite does not validate any specific business logic by checking the
values API methods _may_ return in certain situations. This should be
handled through additional suites local to the manager's implementation.
"""

# pylint: disable=invalid-name, missing-function-docstring

from .harness import FixtureAugmentedTestCase
from ...specifications import EntitySpecification


__all__ = []


class Test_identifier(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.identifier.
    """
    def test_is_correct_type(self):
        self.assertIsInstance(self._manager.identifier(), str)

    def test_is_non_empty(self):
        self.assertIsNot(self._manager.identifier(), "")

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["identifier"], self._manager.identifier())


class Test_displayName(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.displayName.
    """
    def test_is_correct_type(self):
        self.assertIsInstance(self._manager.displayName(), str)

    def test_is_non_empty(self):
        self.assertIsNot(self._manager.displayName(), "")

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["display_name"], self._manager.displayName())


class Test_info(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerAPI.ManagerInterface.info.
    """
    # TODO(DF): Once `isEntityReference` tests are added, check that
    #   `kField_EntityReferencesMatchPrefix` in info dict is used.
    def test_is_correct_type(self):
        self.assertIsStringKeyPrimitiveValueDict(self._manager.info())

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["info"], self._manager.info())


class Test_managementPolicy(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerAPI.ManagerInterface.managementPolicy
    """

    def test_when_called_with_single_specification_returns_single_result(self):
        context = self._session.createContext()
        self.__assertPolicyResults(1, context)

    def test_when_called_with_ten_specifications_returns_ten_results(self):
        context = self._session.createContext()
        self.__assertPolicyResults(10, context)

    def test_calling_with_read_context(self):
        context = self._session.createContext()
        context.access = context.kRead
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_context(self):
        context = self._session.createContext()
        context.access = context.kWrite
        self.__assertPolicyResults(1, context)

    def test_calling_with_read_multiple_context(self):
        context = self._session.createContext()
        context.access = context.kReadMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_multiple_context(self):
        context = self._session.createContext()
        context.access = context.kWriteMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_read_context_and_entity_reference(self):
        context = self._session.createContext()
        context.access = context.kRead
        self.__assertPolicyResults(1, context, self._fixtures['valid_entity_reference'])

    def test_calling_with_write_context_and_entity_reference(self):
        context = self._session.createContext()
        context.access = context.kWrite
        self.__assertPolicyResults(1, context, self._fixtures['valid_entity_reference'])

    def test_calling_with_read_multiple_context_and_entity_reference(self):
        context = self._session.createContext()
        context.access = context.kReadMultiple
        self.__assertPolicyResults(1, context, self._fixtures['valid_entity_reference'])

    def test_calling_with_write_multiple_context_and_entity_reference(self):
        context = self._session.createContext()
        context.access = context.kWriteMultiple
        self.__assertPolicyResults(1, context, self._fixtures['valid_entity_reference'])

    def __assertPolicyResults(self, numSpecifications, context, entityRef=None):
        """
        Tests the validity and coherency of the results of a call to
        `managementPolicy` for a given number of specifications and
        context. It checks lengths match and values are of the correct
        type.
        """
        specs = [EntitySpecification() for _ in range(numSpecifications)]

        policies = self._manager.managementPolicy(specs, context, entityRef=entityRef)

        self.assertValuesOfType(policies, int)
        self.assertEqual(len(policies), numSpecifications)
