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
For example, that when a @fqref{managerApi.ManagerInterface.managementPolicy}
"managementPolicy" query returns a non-ignored state, that there are no
errors calling the other required methods for a managed entity with
those @ref trait "traits".

The suite does not validate any specific business logic by checking the
values API methods _may_ return in certain situations. This should be
handled through additional suites local to the manager's implementation.
"""

# pylint: disable=invalid-name, missing-function-docstring, no-member

from .harness import FixtureAugmentedTestCase
from ... import BatchElementError, Context, EntityReference, TraitsData


__all__ = []


class Test_identifier(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.identifier.
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
    managerApi.ManagerInterface.displayName.
    """

    def test_is_correct_type(self):
        self.assertIsInstance(self._manager.displayName(), str)

    def test_is_non_empty(self):
        self.assertIsNot(self._manager.displayName(), "")

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["display_name"], self._manager.displayName())


class Test_info(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerApi.ManagerInterface.info.
    """

    # TODO(DF): Once `isEntityReferenceString` tests are added, check
    # that `kField_EntityReferencesMatchPrefix` in info dict is used.
    def test_is_correct_type(self):
        self.assertIsStringKeyPrimitiveValueDict(self._manager.info())

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["info"], self._manager.info())


class Test_settings(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerApi.ManagerInterface.settings.
    """

    def test_when_retrieved_settings_modified_then_newly_queried_settings_unmodified(self):
        original = self._manager.settings()
        expected = original.copy()
        original["update"] = 123
        self.assertEqual(self._manager.settings(), expected)


class Test_initialize(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.initialize.
    """

    def setUp(self):
        self.__original_settings = self._manager.settings()

    def tearDown(self):
        self._manager.initialize(self.__original_settings)

    def test_when_settings_are_empty_then_all_settings_unchanged(self):
        expected = self._manager.settings()

        self._manager.initialize({})

        self.assertEqual(self._manager.settings(), expected)

    def test_when_settings_have_invalid_keys_then_raises_KeyError(self):
        invalid_settings = self.requireFixture(
            "some_settings_with_new_values_and_invalid_keys", skipTestIfMissing=True
        )

        with self.assertRaises(KeyError):
            self._manager.initialize(invalid_settings)

    def test_when_settings_have_invalid_keys_then_all_settings_unchanged(self):
        expected = self._manager.settings()
        invalid_settings = self.requireFixture(
            "some_settings_with_new_values_and_invalid_keys", skipTestIfMissing=True
        )

        try:
            self._manager.initialize(invalid_settings)
        except Exception:  # pylint: disable=broad-except
            pass

        self.assertEqual(self._manager.settings(), expected)

    def test_when_settings_have_all_keys_then_all_settings_updated(self):
        updated = self.requireFixture("some_settings_with_all_keys", skipTestIfMissing=True)

        self._manager.initialize(updated)

        self.assertEqual(self._manager.settings(), updated)

    def test_when_settings_have_subset_of_keys_then_other_settings_unchanged(self):
        partial = self.requireFixture(
            "some_settings_with_a_subset_of_keys", skipTestIfMissing=True
        )
        expected = self._manager.settings()
        expected.update(partial)

        self._manager.initialize(partial)

        self.assertEqual(self._manager.settings(), expected)


class Test_managementPolicy(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerApi.ManagerInterface.managementPolicy
    """

    def test_when_called_with_single_trait_set_returns_single_result(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context)

    def test_when_called_with_ten_trait_sets_returns_ten_results(self):
        context = self.createTestContext()
        self.__assertPolicyResults(10, context)

    def test_calling_with_read_context(self):
        context = self.createTestContext()
        context.access = context.Access.kRead
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_context(self):
        context = self.createTestContext()
        context.access = context.Access.kWrite
        self.__assertPolicyResults(1, context)

    def test_calling_with_read_multiple_context(self):
        context = self.createTestContext()
        context.access = context.Access.kReadMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_multiple_context(self):
        context = self.createTestContext()
        context.access = context.Access.kWriteMultiple
        self.__assertPolicyResults(1, context)

    def test_calling_with_empty_trait_set_does_not_error(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, traitSet=set())

    def test_calling_with_unknown_complex_trait_set_does_not_error(self):
        context = self.createTestContext()
        traits = {"🐟🐠🐟🐠", "asdfsdfasdf", "⿂"}
        self.__assertPolicyResults(1, context, traitSet=traits)

    def __assertPolicyResults(self, numTraitSets, context, traitSet={"entity"}):
        """
        Tests the validity and coherency of the results of a call to
        `managementPolicy` for a given number of trait sets and
        context. It checks lengths match and values are of the correct
        type.

        @param traitSet `List[str]` The set of traits to pass to
        the call to managementPolicy.
        """
        # pylint: disable=dangerous-default-value
        traitSets = [traitSet for _ in range(numTraitSets)]

        policies = self._manager.managementPolicy(traitSets, context)

        self.assertValuesOfType(policies, TraitsData)
        self.assertEqual(len(policies), numTraitSets)


class Test_isEntityReferenceString(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.isEntityReferenceString.
    """

    def setUp(self):
        self.collectRequiredFixture("a_valid_reference", skipTestIfMissing=True)
        self.collectRequiredFixture("an_invalid_reference")

    def test_valid_reference_returns_true(self):
        assert self._manager.isEntityReferenceString(self.a_valid_reference) is True

    def test_non_reference_returns_false(self):
        assert self.an_invalid_reference != ""
        assert self._manager.isEntityReferenceString(self.an_invalid_reference) is False

    def test_empty_string_returns_false(self):
        assert self._manager.isEntityReferenceString("") is False

    def test_random_unicode_input_returns_false(self):
        unicode_reference = "🦆🦆🦑"
        assert self._manager.isEntityReferenceString(unicode_reference) is False


class Test_entityExists(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.entityExists.
    """

    def setUp(self):
        self.a_reference_to_an_existing_entity = self._manager.createEntityReference(
            self.requireFixture("a_reference_to_an_existing_entity", skipTestIfMissing=True)
        )
        self.a_reference_to_a_nonexisting_entity = self._manager.createEntityReference(
            self.requireFixture("a_reference_to_a_nonexisting_entity")
        )

    def test_existing_reference_returns_true(self):
        context = self.createTestContext()
        assert self._manager.entityExists([self.a_reference_to_an_existing_entity], context) == [
            True
        ]

    def test_non_existant_reference_returns_false(self):
        context = self.createTestContext()
        assert self._manager.entityExists([self.a_reference_to_a_nonexisting_entity], context) == [
            False
        ]

    def test_mixed_inputs_returns_mixed_output(self):
        existing = self.a_reference_to_an_existing_entity
        nonexistant = self.a_reference_to_a_nonexisting_entity
        context = self.createTestContext()
        assert self._manager.entityExists([existing, nonexistant], context) == [True, False]


class Test_resolve(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.resolve.
    """

    def setUp(self):
        self.a_reference_to_a_readable_entity = self._manager.createEntityReference(
            self.requireFixture("a_reference_to_a_readable_entity", skipTestIfMissing=True)
        )
        self.collectRequiredFixture("a_set_of_valid_traits")

    def test_when_no_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], set(), Context.Access.kRead, set())

    def test_when_multiple_references_then_same_number_of_returned_specifications(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref, ref, ref, ref, ref], set(), Context.Access.kRead, set())

    def test_when_unknown_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], {"₲₪₡🤯"}, Context.Access.kRead, set())

    def test_when_valid_traits_then_returned_specification_has_those_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        self.__testResolution([ref], traits, Context.Access.kRead, traits)

    def test_when_valid_and_unknown_traits_then_returned_specification_only_has_valid_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        mixed_traits = set(traits)
        mixed_traits.add("₲₪₡🤯")
        self.__testResolution([ref], mixed_traits, Context.Access.kRead, traits)

    def test_when_resolving_read_only_reference_for_write_then_access_error_is_returned(self):
        self.__testResolutionError(
            "a_reference_to_a_readonly_entity",
            access=Context.Access.kWrite,
            errorCode=BatchElementError.ErrorCode.kEntityAccessError,
        )

    def test_when_resolving_write_only_reference_for_read_then_access_error_is_returned(self):
        self.__testResolutionError(
            "a_reference_to_a_writeonly_entity",
            access=Context.Access.kRead,
            errorCode=BatchElementError.ErrorCode.kEntityAccessError,
        )

    def test_when_resolving_missing_reference_then_resolution_error_is_returned(self):
        self.__testResolutionError("a_reference_to_a_missing_entity")

    def test_when_resolving_malformed_reference_then_malformed_reference_error_is_returned(self):
        self.__testResolutionError(
            "a_malformed_reference",
            errorCode=BatchElementError.ErrorCode.kMalformedEntityReference,
        )

    def __testResolution(self, references, traits, access, expected_traits):
        context = self.createTestContext()
        context.access = access
        results = []

        self._manager.resolve(
            references,
            traits,
            context,
            lambda _idx, traits_data: results.append(traits_data),
            lambda idx, batch_element_error: self.fail(
                f"Error processing '{references[idx].toString()}': {batch_element_error.message}"
            ),
        )

        self.assertEqual(len(results), len(references))
        for result in results:
            self.assertEqual(result.traitSet(), expected_traits)

    def __testResolutionError(
        self,
        fixture_name,
        access=Context.Access.kRead,
        errorCode=BatchElementError.ErrorCode.kEntityResolutionError,
    ):
        reference = self._manager.createEntityReference(
            self.requireFixture(fixture_name, skipTestIfMissing=True)
        )

        expected_msg = self.requireFixture(f"the_error_string_for_{fixture_name}")
        expected_error = BatchElementError(errorCode, expected_msg)

        context = self.createTestContext()
        context.access = access

        results = []
        self._manager.resolve(
            [reference],
            self.a_set_of_valid_traits,
            context,
            lambda _idx, _traits_data: self.fail("Unexpected success callback"),
            lambda _idx, batch_element_error: results.append(batch_element_error),
        )
        [actual_error] = results  # pylint: disable=unbalanced-tuple-unpacking

        self.assertIsInstance(actual_error, BatchElementError)
        self.assertEqual(actual_error.code, expected_error.code)
        self.assertEqual(actual_error.message, expected_error.message)


class Test_preflight(FixtureAugmentedTestCase):
    """
    Check a plugin's implementation of
    managerApi.ManagerInterface.preflight.
    """

    def setUp(self):
        self.a_reference_to_a_writable_entity = self._manager.createEntityReference(
            self.requireFixture("a_reference_to_a_writable_entity", skipTestIfMissing=True)
        )
        self.collectRequiredFixture("a_set_of_valid_traits")

    def test_when_multiple_references_then_same_number_of_returned_references(self):
        ref = self.a_reference_to_a_writable_entity

        results = []
        self._manager.preflight(
            [ref, ref],
            self.a_set_of_valid_traits,
            self.createTestContext(),
            lambda _, ref: results.append(ref),
            lambda _, err: self.fail(err.message),
        )

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, EntityReference)

    def test_when_reference_is_read_only_then_access_error_is_returned(self):
        self.__testPreflightError(
            "a_reference_to_a_readonly_entity", BatchElementError.ErrorCode.kEntityAccessError
        )

    def test_when_reference_malformed_then_malformed_entity_reference_error_returned(self):
        self.__testPreflightError(
            "a_malformed_reference", BatchElementError.ErrorCode.kMalformedEntityReference
        )

    def __testPreflightError(self, fixture_name, errorCode):
        reference = self._manager.createEntityReference(
            self.requireFixture(fixture_name, skipTestIfMissing=True)
        )

        expected_msg = self.requireFixture(f"the_error_string_for_{fixture_name}")
        expected_error = BatchElementError(errorCode, expected_msg)

        context = self.createTestContext()
        context.access = Context.Access.kWrite

        errors = []
        self._manager.preflight(
            [reference],
            self.a_set_of_valid_traits,
            context,
            lambda _idx, _ref: self.fail("Preflight should not succeed"),
            lambda _idx, error: errors.append(error),
        )
        [actual_error] = errors  # pylint: disable=unbalanced-tuple-unpacking

        self.assertIsInstance(actual_error, BatchElementError)
        self.assertEqual(actual_error.code, expected_error.code)
        self.assertEqual(actual_error.message, expected_error.message)


class Test_register(FixtureAugmentedTestCase):
    """
    Check a plugin's implementation of
    managerApi.ManagerInterface.register.
    """

    def setUp(self):
        self.a_reference_to_a_writable_entity = self._manager.createEntityReference(
            self.requireFixture("a_reference_to_a_writable_entity", skipTestIfMissing=True)
        )
        self.collectRequiredFixture("a_traitsdata_for_a_reference_to_a_writable_entity")

    def test_when_multiple_references_then_same_number_of_returned_references(self):
        ref = self.a_reference_to_a_writable_entity
        data = self.a_traitsdata_for_a_reference_to_a_writable_entity

        results = []
        self._manager.register(
            [ref, ref],
            [data, data],
            self.createTestContext(),
            lambda _, ref: results.append(ref),
            lambda _, err: self.fail(err.message),
        )

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, EntityReference)

    def test_when_reference_is_read_only_then_access_error_is_returned(self):
        self.__testRegisterError(
            "a_reference_to_a_readonly_entity", BatchElementError.ErrorCode.kEntityAccessError
        )

    def test_when_reference_malformed_then_malformed_entity_reference_error_returned(self):
        self.__testRegisterError(
            "a_malformed_reference", BatchElementError.ErrorCode.kMalformedEntityReference
        )

    def __testRegisterError(self, fixture_name, errorCode):
        reference = self._manager.createEntityReference(
            self.requireFixture(fixture_name, skipTestIfMissing=True)
        )

        expected_msg = self.requireFixture(f"the_error_string_for_{fixture_name}")
        expected_error = BatchElementError(errorCode, expected_msg)

        context = self.createTestContext()
        context.access = Context.Access.kWrite

        errors = []
        self._manager.register(
            [reference],
            [self.a_traitsdata_for_a_reference_to_a_writable_entity],
            self.createTestContext(),
            lambda _idx, _ref: self.fail("Preflight should not succeed"),
            lambda _idx, error: errors.append(error),
        )
        [actual_error] = errors  # pylint: disable=unbalanced-tuple-unpacking

        self.assertIsInstance(actual_error, BatchElementError)
        self.assertEqual(actual_error.code, expected_error.code)
        self.assertEqual(actual_error.message, expected_error.message)


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
