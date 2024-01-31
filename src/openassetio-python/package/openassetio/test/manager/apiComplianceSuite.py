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
import copy
import operator
import weakref

# pylint: disable=invalid-name, missing-function-docstring, no-member
# pylint: disable=too-many-lines,unbalanced-tuple-unpacking

from .harness import FixtureAugmentedTestCase
from ... import EntityReference
from ...errors import BatchElementError
from ...access import (
    PolicyAccess,
    ResolveAccess,
    RelationsAccess,
    PublishingAccess,
    EntityTraitsAccess,
)
from ...trait import TraitsData


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
    # that `kInfoKey_EntityReferencesMatchPrefix` in info dict is used.
    def test_is_correct_type(self):
        self.assertIsStringKeyPrimitiveValueDict(self._manager.info())

    def test_matches_fixture(self):
        self.assertEqual(self._fixtures["info"], self._manager.info())


class Test_updateTerminology(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of managerApi.ManagerInterface.updateTerminology.
    """

    def test_output_contains_input_terms(self):
        if not self._manager.hasCapability(self._manager.Capability.kCustomTerminology):
            self.skipTest("kCustomTerminology capability not implemented")

        terms = {"aTermKey🔥 ": "aTermValue🎖️", "aSecondTermKey": "aSecondTermValue"}
        return_terms = self._manager.updateTerminology(terms)
        self.assertEqual(sorted(terms.keys()), sorted(return_terms.keys()))


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
        self.__assertPolicyResults(1, context)

    def test_calling_with_write_context(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, policyAccess=PolicyAccess.kWrite)

    def test_calling_with_createRelated_context(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, policyAccess=PolicyAccess.kCreateRelated)

    def test_calling_with_required_context(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, policyAccess=PolicyAccess.kRequired)

    def test_calling_with_managerDriven_context(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, policyAccess=PolicyAccess.kManagerDriven)

    def test_calling_with_empty_trait_set_does_not_error(self):
        context = self.createTestContext()
        self.__assertPolicyResults(1, context, traitSet=set())

    def test_calling_with_unknown_complex_trait_set_does_not_error(self):
        context = self.createTestContext()
        traits = {"🐟🐠🐟🐠", "asdfsdfasdf", "⿂"}
        self.__assertPolicyResults(1, context, traitSet=traits)

    def __assertPolicyResults(
        self, numTraitSets, context, policyAccess=PolicyAccess.kRead, traitSet={"entity"}
    ):
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

        policies = self._manager.managementPolicy(traitSets, policyAccess, context)

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
        self.a_reference_to_an_existing_entity = self.requireEntityReferenceFixture(
            "a_reference_to_an_existing_entity", skipTestIfMissing=True
        )

    def test_has_capability(self):
        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kExistenceQueries))

    def test_when_querying_existing_reference_then_true_is_returned(self):
        context = self.createTestContext()
        result = [None]
        self._manager.entityExists(
            [self.a_reference_to_an_existing_entity],
            context,
            lambda idx, value: operator.setitem(result, idx, value),
            lambda idx, error: self.fail(f"entityExists should not fail: {error.message}"),
        )
        self.assertEqual(result, [True])

    def test_when_querying_nonexisting_reference_then_false_is_returned(self):
        a_reference_to_a_nonexisting_entity = self.requireEntityReferenceFixture(
            "a_reference_to_a_nonexisting_entity"
        )
        context = self.createTestContext()
        result = [None]
        self._manager.entityExists(
            [a_reference_to_a_nonexisting_entity],
            context,
            lambda idx, value: operator.setitem(result, idx, value),
            lambda idx, error: self.fail(f"entityExists should not fail: {error.message}"),
        )
        self.assertEqual(result, [False])

    def test_when_querying_existing_and_nonexisting_references_then_true_and_false_is_returned(
        self,
    ):
        a_reference_to_a_nonexisting_entity = self.requireEntityReferenceFixture(
            "a_reference_to_a_nonexisting_entity"
        )
        context = self.createTestContext()
        result = [None, None]
        self._manager.entityExists(
            [self.a_reference_to_an_existing_entity, a_reference_to_a_nonexisting_entity],
            context,
            lambda idx, value: operator.setitem(result, idx, value),
            lambda idx, error: self.fail(f"entityExists should not fail: {error.message}"),
        )
        self.assertEqual(result, [True, False])

    def test_when_querying_malformed_reference_then_malformed_reference_error_is_returned(self):
        a_malformed_reference = self.requireEntityReferenceFixture("a_malformed_reference")
        expected_error_message = self.requireFixture("expected_error_message")
        context = self.createTestContext()
        result = [None]
        self._manager.entityExists(
            [a_malformed_reference],
            context,
            lambda idx, value: self.fail("entityExists should not succeed"),
            lambda idx, error: operator.setitem(result, idx, error),
        )
        [error] = result

        self.assertEqual(error.code, BatchElementError.ErrorCode.kMalformedEntityReference)
        self.assertEqual(error.message, expected_error_message)


class Test_entityTraits(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.entityTraits.
    """

    def test_when_querying_malformed_reference_then_malformed_reference_error_is_returned(self):
        a_malformed_reference = self.requireEntityReferenceFixture(
            "a_malformed_reference", skipTestIfMissing=True
        )
        expected_error_message = self.requireFixture("expected_error_message")
        self.__assert_error(
            a_malformed_reference,
            BatchElementError.ErrorCode.kMalformedEntityReference,
            expected_error_message,
        )

    def test_when_querying_missing_reference_for_read_then_resolution_error_is_returned(self):
        a_missing_reference = self.requireEntityReferenceFixture(
            "a_reference_to_a_missing_entity", skipTestIfMissing=True
        )
        expected_error_message = self.requireFixture("expected_error_message")
        self.__assert_error(
            a_missing_reference,
            BatchElementError.ErrorCode.kEntityResolutionError,
            expected_error_message,
        )

    def test_when_read_only_entity_queried_for_write_then_access_error_is_returned(self):
        a_readonly_reference = self.requireEntityReferenceFixture(
            "a_reference_to_a_readonly_entity", skipTestIfMissing=True
        )
        expected_error_message = self.requireFixture("expected_error_message")
        self.__assert_error(
            a_readonly_reference,
            BatchElementError.ErrorCode.kEntityAccessError,
            expected_error_message,
            entity_traits_access=EntityTraitsAccess.kWrite,
        )

    def test_when_write_only_entity_queried_for_read_then_access_error_is_returned(self):
        a_writeonly_reference = self.requireEntityReferenceFixture(
            "a_reference_to_a_writeonly_entity", skipTestIfMissing=True
        )
        expected_error_message = self.requireFixture("expected_error_message")
        self.__assert_error(
            a_writeonly_reference,
            BatchElementError.ErrorCode.kEntityAccessError,
            expected_error_message,
            entity_traits_access=EntityTraitsAccess.kRead,
        )

    def test_when_multiple_references_for_read_then_same_number_of_returned_trait_sets(self):
        first_ref = self.requireEntityReferenceFixture(
            "first_entity_reference", skipTestIfMissing=True
        )
        first_trait_set = self.requireFixture("first_entity_trait_set")

        second_ref = self.requireEntityReferenceFixture("second_entity_reference")
        second_trait_set = self.requireFixture("second_entity_trait_set")

        self.__assert_multiple_references(
            EntityTraitsAccess.kRead,
            first_ref,
            first_trait_set,
            second_ref,
            second_trait_set,
        )

    def test_when_multiple_references_for_write_then_same_number_of_returned_trait_sets(self):
        first_ref = self.requireEntityReferenceFixture(
            "first_entity_reference", skipTestIfMissing=True
        )
        first_trait_set = self.requireFixture("first_entity_trait_set")

        second_ref = self.requireEntityReferenceFixture("second_entity_reference")
        second_trait_set = self.requireFixture("second_entity_trait_set")

        self.__assert_multiple_references(
            EntityTraitsAccess.kWrite,
            first_ref,
            first_trait_set,
            second_ref,
            second_trait_set,
        )

    def __assert_multiple_references(
        self,
        entity_traits_access,
        first_ref,
        first_trait_set,
        second_ref,
        second_trait_set,
    ):
        assert (
            first_ref != second_ref
        ), "Fixture error: first/second_entity_reference must be distinct"
        assert (
            first_trait_set != second_trait_set
        ), "Fixture error: first/second_entity_trait_set must be distinct"

        # Some arbitrary order that's unlikely to be replicated by chance.
        entity_references = [second_ref, first_ref, first_ref, second_ref, first_ref]
        expected_trait_sets = [
            second_trait_set,
            first_trait_set,
            first_trait_set,
            second_trait_set,
            first_trait_set,
        ]

        context = self.createTestContext()
        actual_trait_sets = [None] * len(entity_references)

        self._manager.entityTraits(
            entity_references,
            entity_traits_access,
            context,
            lambda idx, value: operator.setitem(actual_trait_sets, idx, value),
            lambda idx, error: self.fail("entityTraits should not fail"),
        )

        self.assertListEqual(actual_trait_sets, expected_trait_sets)

    def __assert_error(
        self,
        entity_reference,
        expected_error_code,
        expected_error_message,
        entity_traits_access=EntityTraitsAccess.kRead,
    ):
        context = self.createTestContext()
        result = [None]
        self._manager.entityTraits(
            [entity_reference],
            entity_traits_access,
            context,
            lambda idx, value: self.fail("entityTraits should not succeed"),
            lambda idx, error: operator.setitem(result, idx, error),
        )
        [error] = result

        self.assertEqual(error.code, expected_error_code)
        self.assertEqual(error.message, expected_error_message)


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

    def test_has_capability(self):
        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kResolution))

    def test_when_no_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], set(), ResolveAccess.kRead, set())

    def test_when_multiple_references_then_same_number_of_returned_specifications(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref, ref, ref, ref, ref], set(), ResolveAccess.kRead, set())

    def test_when_unknown_traits_then_returned_specification_is_empty(self):
        ref = self.a_reference_to_a_readable_entity
        self.__testResolution([ref], {"₲₪₡🤯"}, ResolveAccess.kRead, set())

    def test_when_valid_traits_then_returned_specification_has_those_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        self.__testResolution([ref], traits, ResolveAccess.kRead, traits)

    def test_when_valid_and_unknown_traits_then_returned_specification_only_has_valid_traits(self):
        ref = self.a_reference_to_a_readable_entity
        traits = self.a_set_of_valid_traits
        mixed_traits = set(traits)
        mixed_traits.add("₲₪₡🤯")
        self.__testResolution([ref], mixed_traits, ResolveAccess.kRead, traits)

    def test_when_resolving_read_only_reference_for_publish_then_access_error_is_returned(self):
        self.__testResolutionError(
            "a_reference_to_a_readonly_entity",
            resolve_access=ResolveAccess.kManagerDriven,
            errorCode=BatchElementError.ErrorCode.kEntityAccessError,
        )

    def test_when_resolving_write_only_reference_for_read_then_access_error_is_returned(self):
        self.__testResolutionError(
            "a_reference_to_a_writeonly_entity",
            resolve_access=ResolveAccess.kRead,
            errorCode=BatchElementError.ErrorCode.kEntityAccessError,
        )

    def test_when_resolving_missing_reference_then_resolution_error_is_returned(self):
        self.__testResolutionError("a_reference_to_a_missing_entity")

    def test_when_resolving_malformed_reference_then_malformed_reference_error_is_returned(self):
        self.__testResolutionError(
            "a_malformed_reference",
            errorCode=BatchElementError.ErrorCode.kMalformedEntityReference,
        )

    def __testResolution(self, references, traits, resolve_access, expected_traits):
        context = self.createTestContext()
        results = []

        self._manager.resolve(
            references,
            traits,
            resolve_access,
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
        resolve_access=ResolveAccess.kRead,
        errorCode=BatchElementError.ErrorCode.kEntityResolutionError,
    ):
        reference = self._manager.createEntityReference(
            self.requireFixture(fixture_name, skipTestIfMissing=True)
        )

        expected_msg = self.requireFixture(f"the_error_string_for_{fixture_name}")
        expected_error = BatchElementError(errorCode, expected_msg)

        context = self.createTestContext()

        results = []
        self._manager.resolve(
            [reference],
            self.a_set_of_valid_traits,
            resolve_access,
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

    def test_has_capability(self):
        self.requireFixture("a_traits_data_for_preflight", skipTestIfMissing=True)
        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kPublishing))

    def test_when_multiple_references_then_same_number_of_returned_references(self):
        traits_data = self.requireFixture("a_traits_data_for_preflight", skipTestIfMissing=True)
        entity_reference = self.requireEntityReferenceFixture("a_reference_for_preflight")

        results = []
        self._manager.preflight(
            [entity_reference, entity_reference],
            [traits_data, traits_data],
            PublishingAccess.kWrite,
            self.createTestContext(),
            lambda _, ref: results.append(ref),
            lambda _, err: self.fail(err.message),
        )

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, EntityReference)

    def test_when_reference_is_read_only_then_access_error_is_returned(self):
        traits_data = self.requireFixture("a_traits_data_for_preflight", skipTestIfMissing=True)
        entity_reference = self.requireEntityReferenceFixture("a_reference_to_a_readonly_entity")
        expected_error_message = self.requireFixture("expected_error_message")
        self.__testPreflightError(
            entity_reference,
            traits_data,
            expected_error_message,
            BatchElementError.ErrorCode.kEntityAccessError,
        )

    def test_when_reference_malformed_then_malformed_entity_reference_error_returned(self):
        traits_data = self.requireFixture("a_traits_data_for_preflight", skipTestIfMissing=True)
        entity_reference = self.requireEntityReferenceFixture("a_malformed_reference")
        expected_error_message = self.requireFixture("expected_error_message")
        self.__testPreflightError(
            entity_reference,
            traits_data,
            expected_error_message,
            BatchElementError.ErrorCode.kMalformedEntityReference,
        )

    def test_when_preflight_hint_invalid_then_invalid_preflight_hint_error_returned(self):
        traits_data = self.requireFixture(
            "an_invalid_traits_data_for_preflight", skipTestIfMissing=True
        )
        entity_reference = self.requireEntityReferenceFixture("a_reference_for_preflight")
        expected_error_message = self.requireFixture("expected_error_message")
        self.__testPreflightError(
            entity_reference,
            traits_data,
            expected_error_message,
            BatchElementError.ErrorCode.kInvalidPreflightHint,
        )

    def __testPreflightError(
        self, entity_reference, traits_data, expected_error_message, expected_error_code
    ):
        expected_error = BatchElementError(expected_error_code, expected_error_message)

        context = self.createTestContext()

        errors = []
        self._manager.preflight(
            [entity_reference],
            [traits_data],
            PublishingAccess.kWrite,
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

    def test_has_capability(self):
        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kPublishing))

    def test_when_multiple_references_then_same_number_of_returned_references(self):
        ref = self.a_reference_to_a_writable_entity
        data = self.a_traitsdata_for_a_reference_to_a_writable_entity

        results = []
        self._manager.register(
            [ref, ref],
            [data, data],
            PublishingAccess.kWrite,
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

        errors = []
        self._manager.register(
            [reference],
            [self.a_traitsdata_for_a_reference_to_a_writable_entity],
            PublishingAccess.kWrite,
            self.createTestContext(),
            lambda _idx, _ref: self.fail("Preflight should not succeed"),
            lambda _idx, error: errors.append(error),
        )
        [actual_error] = errors  # pylint: disable=unbalanced-tuple-unpacking

        self.assertIsInstance(actual_error, BatchElementError)
        self.assertEqual(actual_error.code, expected_error.code)
        self.assertEqual(actual_error.message, expected_error.message)


class Test_getWithRelationship_All(FixtureAugmentedTestCase):
    """
    Check plugin's implementation of
    managerApi.ManagerInterface.getWithRelationship[s]
    """

    def test_when_relation_unknown_then_no_pages_returned(self):
        a_ref = self.requireEntityReferenceFixture("a_reference", skipTestIfMissing=True)
        an_unknown_rel = TraitsData({"🐠🐟🐠🐟"})

        with self.subTest("getWithRelationship"):
            [pager] = self.__test_getWithRelationship_success([a_ref], an_unknown_rel)
            self.__assert_pager_is_at_end(pager)

        with self.subTest("getWithRelationships"):
            [pager] = self.__test_getWithRelationships_success(a_ref, [an_unknown_rel])
            self.__assert_pager_is_at_end(pager)

    def test_has_capability(self):
        self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True)
        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kRelationshipQueries))

    def test_when_batched_then_same_number_of_returned_relationships(self):
        a_rel = TraitsData(self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True))
        a_ref = self.requireEntityReferenceFixture("a_reference")

        with self.subTest("getWithRelationship"):
            pagers = self.__test_getWithRelationship_success([a_ref] * 5, a_rel)
            self.assertEqual(len(pagers), 5)

        with self.subTest("getWithRelationships"):
            pagers = self.__test_getWithRelationships_success(a_ref, [a_rel] * 5)
            self.assertEqual(len(pagers), 5)

    def test_when_relationship_trait_set_known_then_all_with_trait_set_returned(self):
        a_rel = TraitsData(self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True))
        a_ref = self.requireEntityReferenceFixture("a_reference")
        expected = self.requireEntityReferencesFixture("expected_related_entity_references")

        with self.subTest("getWithRelationship"):
            [pager] = self.__test_getWithRelationship_success([a_ref], a_rel)
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

        with self.subTest("getWithRelationships"):
            [pager] = self.__test_getWithRelationships_success(a_ref, [a_rel])
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

    def test_when_relationship_trait_set_known_and_props_set_then_filtered_refs_returned(self):
        a_rel = self.requireFixture(
            "a_relationship_traits_data_with_props", skipTestIfMissing=True
        )
        a_ref = self.requireEntityReferenceFixture("a_reference")
        expected = self.requireEntityReferencesFixture("expected_related_entity_references")

        with self.subTest("getWithRelationship"):
            [pager] = self.__test_getWithRelationship_success([a_ref], a_rel)
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

        with self.subTest("getWithRelationships"):
            [pager] = self.__test_getWithRelationships_success(a_ref, [a_rel])
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

    def test_when_result_trait_set_supplied_then_filtered_refs_returned(self):
        a_rel = TraitsData(self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True))
        a_ref = self.requireEntityReferenceFixture("a_reference")
        result_trait_set = self.requireFixture("an_entity_trait_set_to_filter_by")
        expected = self.requireEntityReferencesFixture("expected_related_entity_references")

        with self.subTest("getWithRelationship"):
            [pager] = self.__test_getWithRelationship_success(
                [a_ref], a_rel, resultTraitSet=result_trait_set
            )
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

        with self.subTest("getWithRelationships"):
            [pager] = self.__test_getWithRelationships_success(
                a_ref, [a_rel], resultTraitSet=result_trait_set
            )
            actual = self.__concat_all_pages(pager)
            self.assertListEqual(actual, expected)

    def test_when_querying_missing_reference_then_resolution_error_is_returned(self):
        relationship_trait_set = self.requireFixture(
            "a_relationship_trait_set", skipTestIfMissing=True
        )
        entity_reference = self.requireEntityReferenceFixture("a_reference_to_a_missing_entity")
        expected_error_code = BatchElementError.ErrorCode.kEntityResolutionError
        expected_error_message = self.requireFixture("expected_error_message")

        with self.subTest("getWithRelationship"):
            self.__test_getWithRelationship_error(
                entity_reference,
                relationship_trait_set,
                expected_error_code,
                expected_error_message,
            )

        with self.subTest("getWithRelationships"):
            self.__test_getWithRelationships_error(
                entity_reference,
                relationship_trait_set,
                expected_error_code,
                expected_error_message,
            )

    def test_when_querying_malformed_reference_then_malformed_reference_error_is_returned(self):
        relationship_trait_set = self.requireFixture(
            "a_relationship_trait_set", skipTestIfMissing=True
        )
        entity_reference = self.requireEntityReferenceFixture("a_malformed_reference")
        expected_error_code = BatchElementError.ErrorCode.kMalformedEntityReference
        expected_error_message = self.requireFixture("expected_error_message")

        with self.subTest("getWithRelationship"):
            self.__test_getWithRelationship_error(
                entity_reference,
                relationship_trait_set,
                expected_error_code,
                expected_error_message,
            )

        with self.subTest("getWithRelationships"):
            self.__test_getWithRelationships_error(
                entity_reference,
                relationship_trait_set,
                expected_error_code,
                expected_error_message,
            )

    def test_when_related_entities_span_multiple_pages_then_pager_has_multiple_pages(self):
        a_rel = TraitsData(self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True))
        a_ref = self.requireEntityReferenceFixture("a_reference")
        expected_related_refs = self.requireEntityReferencesFixture(
            "expected_related_entity_references"
        )

        # Ensure we have at least two related references, so that we can
        # ensure at least two pages given a page size of 1.
        self.assertGreater(
            len(expected_related_refs),
            1,
            msg="Please provide fixtures that result in at least two related references",
        )

        def test_for_page_size(page_size, get_pagers):
            # Split expected related references list into pages.
            expected_pages = [
                expected_related_refs[page_start : page_start + page_size]
                for page_start in range(0, len(expected_related_refs), page_size)
            ]
            # Expect all True `hasNext()`, except when on the last
            # page.
            expected_hasNexts = [True] * (len(expected_pages) - 1) + [False]

            # Get pager from method under test
            [pager] = get_pagers()

            # Guarantee a non-empty pager. An empty pager would
            # cause a hard-to-discern error in the `zip` call below.
            self.assertListEqual(pager.get(), expected_pages[0])

            # Gather the pages and the result of `hasNext()` during
            # iteration.
            actual = (
                (page, pager.get(), pager.hasNext()) for page in self.__pager_page_iter(pager)
            )
            actual_pages, actual_pages_again, actual_hasNexts = map(list, zip(*actual))

            self.assertListEqual(actual_pages, actual_pages_again)
            self.assertListEqual(actual_pages, expected_pages)
            self.assertListEqual(actual_hasNexts, expected_hasNexts)
            self.__assert_pager_is_at_end(pager)

        for page_size in (1, 2):
            with self.subTest("getWithRelationship", page_size=page_size):
                test_for_page_size(
                    page_size,
                    lambda pageSize=page_size: self.__test_getWithRelationship_success(
                        [a_ref], a_rel, pageSize=pageSize
                    ),
                )
            with self.subTest("getWithRelationships", page_size=page_size):
                test_for_page_size(
                    page_size,
                    lambda pageSize=page_size: self.__test_getWithRelationships_success(
                        a_ref, [a_rel], pageSize=pageSize
                    ),
                )

    class weaklist(list):
        """
        Built-in `list` type does not support weakref, so create
        this shim.
        """

        __slots__ = ("__weakref__",)

    def test_when_pager_constructed_then_no_references_to_original_args_are_retained(self):
        # Wrap pager construction in a function, so that input args can
        # fall out of scope.
        def get_pager_and_weakref_args(get_pagers):
            relationship = TraitsData(
                self.requireFixture("a_relationship_trait_set", skipTestIfMissing=True)
            )
            relationships = self.weaklist([relationship])
            ref = self.requireEntityReferenceFixture("a_reference")
            refs = self.weaklist([ref])
            context = self.createTestContext()
            context.locale = TraitsData(context.locale)  # Force a copy.
            result_trait_set = copy.copy(self.requireFixture("an_entity_trait_set_to_filter_by"))

            [pager] = get_pagers(refs, relationships, context, result_trait_set)

            return (
                pager,
                weakref.ref(ref),
                weakref.ref(refs),
                weakref.ref(relationship),
                weakref.ref(relationships),
                weakref.ref(context),
                weakref.ref(context.locale),
                weakref.ref(result_trait_set),
            )

        with self.subTest("getWithRelationship"):
            _pager, *weak_args = get_pager_and_weakref_args(
                lambda refs, relationships, context, result_trait_set:
                # Call method to get pager under test.
                self.__test_getWithRelationship_success(
                    refs, relationships[0], context=context, resultTraitSet=result_trait_set
                )
            )
            # Use a list comparison so that failing elements are easier
            # to discern in the error output.
            living_args = [weak_arg() for weak_arg in weak_args]
            self.assertListEqual(living_args, [None] * len(living_args))

        with self.subTest("getWithRelationships"):
            _pager, *weak_args = get_pager_and_weakref_args(
                lambda refs, relationships, context, result_trait_set:
                # Call method to get pager under test.
                self.__test_getWithRelationships_success(
                    refs[0], relationships, context=context, resultTraitSet=result_trait_set
                )
            )
            # Use a list comparison so that failing elements are easier
            # to discern in the error output.
            living_args = [weak_arg() for weak_arg in weak_args]
            self.assertListEqual(living_args, [None] * len(living_args))

    def __test_getWithRelationship_success(
        self, references, relationship, pageSize=10, context=None, resultTraitSet=None
    ):
        if context is None:
            context = self.createTestContext()

        if resultTraitSet is None:
            resultTraitSet = set()

        pagers = [None] * len(references)

        self._manager.getWithRelationship(
            references,
            relationship,
            pageSize,
            RelationsAccess.kRead,
            context,
            lambda idx, pager: operator.setitem(pagers, idx, pager),
            lambda idx, batch_element_error: self.fail(
                f"getWithRelationship should not error for: '{references[idx].toString()}': "
                f"{batch_element_error.message}"
            ),
            resultTraitSet,
        )

        self.assertTrue(all(pager is not None for pager in pagers))
        return pagers

    def __test_getWithRelationships_success(
        self, reference, relationships, pageSize=10, context=None, resultTraitSet=None
    ):
        if context is None:
            context = self.createTestContext()

        if resultTraitSet is None:
            resultTraitSet = set()

        pagers = [None] * len(relationships)

        self._manager.getWithRelationships(
            reference,
            relationships,
            pageSize,
            RelationsAccess.kRead,
            context,
            lambda idx, pager: operator.setitem(pagers, idx, pager),
            lambda idx, batch_element_error: self.fail(
                f"getWithRelationships should not error for index {idx}: "
                f"{batch_element_error.message}"
            ),
            resultTraitSet,
        )

        self.assertTrue(all(pager is not None for pager in pagers))
        return pagers

    def __test_getWithRelationship_error(
        self,
        entity_reference,
        relationship_trait_set,
        expected_error_code,
        expected_error_message,
    ):
        expected_error = BatchElementError(expected_error_code, expected_error_message)

        context = self.createTestContext()

        relationship = TraitsData(relationship_trait_set)

        results = []

        self._manager.getWithRelationship(
            [entity_reference],
            relationship,
            1,
            RelationsAccess.kRead,
            context,
            lambda _idx, _pager: self.fail("Unexpected success callback"),
            lambda _idx, batch_element_error: results.append(batch_element_error),
        )
        [actual_error] = results  # pylint: disable=unbalanced-tuple-unpacking

        self.assertEqual(actual_error, expected_error)

    def __test_getWithRelationships_error(
        self,
        entity_reference,
        relationship_trait_set,
        expected_error_code,
        expected_error_message,
    ):
        expected_error = BatchElementError(expected_error_code, expected_error_message)

        context = self.createTestContext()

        relationship = TraitsData(relationship_trait_set)

        results = []

        self._manager.getWithRelationships(
            entity_reference,
            [relationship],
            1,
            RelationsAccess.kRead,
            context,
            lambda _idx, _pager: self.fail("Unexpected success callback"),
            lambda _idx, batch_element_error: results.append(batch_element_error),
        )
        [actual_error] = results  # pylint: disable=unbalanced-tuple-unpacking

        self.assertEqual(actual_error, expected_error)

    def __assert_pager_is_at_end(self, pager):
        self.assertListEqual(pager.get(), [])
        self.assertFalse(pager.hasNext())
        pager.next()
        self.assertListEqual(pager.get(), [])
        self.assertFalse(pager.hasNext())
        pager.next()
        self.assertListEqual(pager.get(), [])
        self.assertFalse(pager.hasNext())

    @classmethod
    def __concat_all_pages(cls, pager):
        return list(cls.__pager_elems_iter(pager))

    @classmethod
    def __pager_elems_iter(cls, pager):
        for page in cls.__pager_page_iter(pager):
            for elem in page:
                yield elem

    @staticmethod
    def __pager_page_iter(pager):
        page = pager.get()
        while page:
            yield page
            pager.next()
            page = pager.get()


class Test_createChildState(FixtureAugmentedTestCase):
    """
    Tests that the createChildState method is implemented if createState
    has been implemented to return a custom state object.
    """

    def test_when_createState_implemented_then_createChildState_returns_state(self):
        context = self._manager.createContext()
        if not context.managerState:
            self.skipTest("createState returned None")

        self.assertTrue(self._manager.hasCapability(self._manager.Capability.kStatefulContexts))

        child_context = self._manager.createChildContext(context)
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
