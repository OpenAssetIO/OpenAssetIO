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
errors calling the other required methods for a managed entity with
those @ref trait "traits".

The suite does not validate any specific business logic by checking the
values API methods _may_ return in certain situations. This should be
handled through additional suites local to the manager's implementation.
"""

# pylint: disable=invalid-name, missing-function-docstring, no-member

from .harness import FixtureAugmentedTestCase
from ...exceptions import EntityResolutionError
from ... import Context


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

class Test_setSettings(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.setSettings.
    """
    def setUp(self):
        self.collectRequiredFixture('some_settings_with_valid_keys', skipTestIfMissing=True)

    def test_valid_settings_succeeds(self):
        self._manager.setSettings(self.some_settings_with_valid_keys)

    def test_unknown_settings_keys_raise_KeyError(self):
        unknown_settings = self.requireFixture("some_settings_with_invalid_keys")
        with self.assertRaises(KeyError):
            self._manager.setSettings(unknown_settings)


class Test_getSettings(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerAPI.ManagerInterface.getSettings.
    """

    def test_when_set_then_get_returns_updated_settings(self):
        updated = self.requireFixture("some_new_settings_with_all_keys", skipTestIfMissing=True)
        self._manager.setSettings(updated)
        self.assertEqual(self._manager.getSettings(), updated)

    def test_when_set_with_subset_then_other_settings_unchanged(self):
        partial = self.requireFixture(
                "some_new_settings_with_a_subset_of_keys", skipTestIfMissing=True)
        settings = self._manager.getSettings()
        self._manager.setSettings(partial)
        settings.update(partial)
        self.assertEqual(self._manager.getSettings(), settings)


class Test_managementPolicy(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerAPI.ManagerInterface.managementPolicy
    """

    def test_when_called_with_single_trait_set_returns_single_result(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context)

    def test_when_called_with_ten_trait_sets_returns_ten_results(self):
        context = self.createTestContext()
        self.__assertPolicyResults(10, context)

    def test_calling_with_read_context(self):
        context = self.createTestContext()
        context.access = context.kRead
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_context(self):
        context = self.createTestContext()
        context.access = context.kWrite
        self.__assertPolicyResults(1, context)

    def test_calling_with_read_multiple_context(self):
        context = self.createTestContext()
        context.access = context.kReadMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_multiple_context(self):
        context = self.createTestContext()
        context.access = context.kWriteMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_empty_trait_set_does_not_error(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, traitSet=())

    def test_calling_with_unknown_complex_trait_set_does_not_error(self):
        context = self.createTestContext()
        traits = ("🐟🐠🐟🐠", "asdfsdfasdf", "⿂")
        self.__assertPolicyResults(1, context, traitSet=traits)

    def __assertPolicyResults(self, numTraitSets, context, traitSet=("entity",)):
        """
        Tests the validity and coherency of the results of a call to
        `managementPolicy` for a given number of trait sets and
        context. It checks lengths match and values are of the correct
        type.

        @param traitSet `List[str]` The set of traits to pass to
        the call to managementPolicy.
        """
        traitSets = [traitSet for _ in range(numTraitSets)]

        policies = self._manager.managementPolicy(traitSets, context)

        self.assertValuesOfType(policies, int)
        self.assertEqual(len(policies), numTraitSets)


class Test_isEntityReference(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.isEntityReference.
    """

    def setUp(self):
        self.collectRequiredFixture("a_valid_reference", skipTestIfMissing=True)
        self.collectRequiredFixture("a_malformed_reference")

    def test_valid_reference_returns_true(self):
        assert self._manager.isEntityReference([self.a_valid_reference]) == [True]

    def test_non_reference_returns_false(self):
        assert self.a_malformed_reference != ""
        assert self._manager.isEntityReference([self.a_malformed_reference]) == [False]

    def test_empty_string_returns_false(self):
        assert self._manager.isEntityReference([""]) == [False]

    def test_mixed_inputs_returns_mixed_output(self):
        reference = self.a_valid_reference
        non_reference = self.a_malformed_reference
        expected = [True, False]
        assert self._manager.isEntityReference([reference, non_reference]) == expected

    def test_random_unicode_input_returns_false(self):
        unicode_reference = "🦆🦆🦑"
        assert self._manager.isEntityReference([unicode_reference]) == [False]


class Test_entityExists(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.entityExists.
    """

    def setUp(self):
        self.collectRequiredFixture("a_reference_to_an_existing_entity", skipTestIfMissing=True)
        self.collectRequiredFixture("a_reference_to_a_nonexisting_entity")

    def test_existing_reference_returns_true(self):
        context = self.createTestContext()
        assert self._manager.entityExists(
                [self.a_reference_to_an_existing_entity], context) == [True]

    def test_non_existant_reference_returns_false(self):
        context = self.createTestContext()
        assert self._manager.entityExists(
                [self.a_reference_to_a_nonexisting_entity], context) == [False]

    def test_mixed_inputs_returns_mixed_output(self):
        existing = self.a_reference_to_an_existing_entity
        nonexistant = self.a_reference_to_a_nonexisting_entity
        context = self.createTestContext()
        assert self._manager.entityExists([existing, nonexistant], context) == [True, False]


class Test_resolve(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerAPI.ManagerInterface.resolve.
    """
    def setUp(self):
        self.collectRequiredFixture("a_reference_to_a_readable_entity", skipTestIfMissing=True)
        self.collectRequiredFixture("a_set_of_valid_traits")

    def test_when_no_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], set(), Context.kRead, set())

    def test_when_multiple_references_then_same_number_of_returned_specifications(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref, ref, ref, ref, ref], set(), Context.kRead, set())

    def test_when_unknown_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], {"₲₪₡🤯"}, Context.kRead, set())

    def test_when_valid_traits_then_returned_specification_has_those_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        self.__testResolution([ref], traits, Context.kRead, traits)

    def test_when_valid_and_unknown_traits_then_returned_specification_only_has_valid_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        mixed_traits = set(traits)
        mixed_traits.add("₲₪₡🤯")
        self.__testResolution([ref], mixed_traits, Context.kRead, traits)

    def test_when_resolving_read_only_reference_for_write_then_resolution_error_is_returned(self):
        self.__testResolutionError("a_reference_to_a_readonly_entity", Context.kWrite)

    def test_when_resolving_write_only_reference_for_read_then_resolution_error_is_returned(self):
        self.__testResolutionError("a_reference_to_a_writeonly_entity", Context.kRead)

    def __testResolution(self, references, traits, access, expected_traits):
        context = self.createTestContext()
        context.access = access
        results = self._manager.resolve(references, traits, context)
        self.assertEqual(len(results), len(references))
        for result in results:
            self.assertEqual(result.traitSet(), expected_traits)

    def __testResolutionError(self, fixture_name, access):
        reference = self.requireFixture(fixture_name, skipTestIfMissing=True)
        expected_msg = self.requireFixture(f"the_error_string_for_{fixture_name}")
        expected_error = EntityResolutionError(expected_msg, reference)
        context = self.createTestContext()
        context.access = access
        [result] = self._manager.resolve([reference], self.a_set_of_valid_traits, context)
        self.assertIsInstance(result, EntityResolutionError)
        self.assertEqual(str(result), str(expected_error))


class Test_createChildState(FixtureAugmentedTestCase):
    """
    Tests that the createChildState method is implemented if createState
    has been implemented to return a custom state object.
    """
    def test_when_createState_implemented_then_createChildState_returns_state(self):
        context = self._manager.createContext()
        if not context.managerState:
            self.skipTest("createState returned None")

        child_context = self._manager.createChildState(context)
        self.assertIsNotNone(child_context.managerState)


class Test_persistenceTokenForState(FixtureAugmentedTestCase):
    """
    Tests that the persistenceTokenForState method is implemented if
    createState has been implemented to return a custom state object.
    """
    def test_when_createState_implemented_then_persistenceTokenForState_returns_string(self):
        context = self._manager.createContext()
        if not context.managerState:
            self.skipTest("createState returned None")

        token = self._manager.persistenceTokenForContext(context)
        self.assertIsInstance(token, str)


class Test_stateFromPersistenceToken(FixtureAugmentedTestCase):
    """
    Tests that the persistenceTokenForState method is implemented if
    createState has been implemented to return a custom state object.
    """
    def test_when_createState_implemented_then_stateFromPersistenceToken_returns_state(self):
        context = self._manager.createContext()
        if not context.managerState:
            self.skipTest("createState returned None")

        token = self._manager.persistenceTokenForContext(context)

        restored_context = self._manager.contextFromPersistenceToken(token)
        self.assertIsNotNone(restored_context.managerState)
