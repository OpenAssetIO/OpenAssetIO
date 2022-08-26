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
A manager test harness test case suite that validates that the
BasicAssetLibrary manager behaves with the correct business logic.
"""

# pylint: disable=invalid-name, missing-function-docstring, missing-class-docstring

import operator
import os

from openassetio import Context, TraitsData
from openassetio.traits.managementPolicy import ManagedTrait
from openassetio.test.manager.harness import FixtureAugmentedTestCase


__all__ = []


class Test_managementPolicy_default_behavior(FixtureAugmentedTestCase):
    """
    Tests that by default, the BAL manages all entities, for read, but
    nothing for write.
    """

    __trait_sets = (
        {"blob", "image"},
        {"container", "shot", "frame_ranged"},
        {"definitely_unique"},
    )

    def test_returns_cooperative_policy_for_read_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.Access.kRead)
        policies = self._manager.managementPolicy(self.__trait_sets, context)
        for policy in policies:
            managedTrait = ManagedTrait(policy)
            self.assertTrue(managedTrait.isValid())
            self.assertIsNone(managedTrait.getExclusive())

    def test_returns_cooperative_policy_for_write_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.Access.kWrite)
        policies = self._manager.managementPolicy(self.__trait_sets, context)
        for policy in policies:
            self.assertTrue(policy.hasTrait(ManagedTrait.kId))


class Test_managementPolicy_library_specified_behavior(FixtureAugmentedTestCase):
    """
    Tests that custom policies are loaded and respected.
    """

    __read_trait_sets = (
        {"definitely", "unique"},
        {"an", "ignored", "trait", "set"},
        {"a", "non", "exclusive", "trait", "set"},
    )

    __write_trait_sets = (
        {"definitely", "unique"},
        {"a", "managed", "trait", "set"},
    )

    # We need to load a different library for these tests. This is
    # a little fiddly as the manager isn't (currently) recreated
    # for each test.

    ## @todo Extend openassetio.test.manager to allow settings to be
    ## varied per test class/method.

    def setUp(self):
        self.__old_settings = self._manager.settings()
        new_settings = self.__old_settings.copy()
        new_settings["library_path"] = os.path.join(
            os.path.dirname(__file__),
            "resources",
            "library_business_logic_suite_customManagementPolicy.json",
        )
        self._manager.initialize(new_settings)

    def tearDown(self):
        self._manager.initialize(self.__old_settings)

    def test_returns_expected_policies_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.Access.kRead)
        expected = [TraitsData({ManagedTrait.kId}), TraitsData(), TraitsData({ManagedTrait.kId})]
        ManagedTrait(expected[0]).setExclusive(True)

        actual = self._manager.managementPolicy(self.__read_trait_sets, context)

        self.assertListEqual(actual, expected)

    def test_returns_expected_policy_for_write_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.Access.kWrite)
        expected = [TraitsData(), TraitsData({ManagedTrait.kId})]

        actual = self._manager.managementPolicy(self.__write_trait_sets, context)

        self.assertListEqual(actual, expected)


class Test_resolve(FixtureAugmentedTestCase):
    """
    Tests that resolution returns the expected values.
    """

    __entities = {
        "bal:///anAsset⭐︎": {
            "string": {"value": "resolved from 'anAsset⭐︎' using 📠"},
            "number": {"value": 42},
            "test-data": {},
        },
        "bal:///another 𝓐𝓼𝓼𝓼𝓮𝔱": {
            "string": {"value": "resolved from 'another 𝓐𝓼𝓼𝓼𝓮𝔱' with a 📟"},
            "number": {},
        },
    }

    def test_when_refs_found_then_success_callback_called_with_expected_values(self):
        entity_references = [
            self._manager.createEntityReference(ref_str) for ref_str in self.__entities
        ]
        trait_set = {"string", "number", "test-data"}
        context = self.createTestContext(access=Context.Access.kRead)

        results = [None] * len(entity_references)

        def success_cb(idx, traits_data):
            results[idx] = traits_data

        def error_cb(idx, batchElementError):
            self.fail(
                f"Unexpected error for '{entity_references[idx].toString()}':"
                f" {batchElementError.message}")

        self._manager.resolve(
            entity_references, trait_set, context, success_cb, error_cb)

        for ref, result in zip(entity_references, results):
            # Check all traits are present, and their properties.
            # TODO(tc): When we have a better introspection API in
            # TraitsData, we can assert there aren't any bonus values.
            for trait in self.__entities[ref.toString()].keys():
                self.assertTrue(result.hasTrait(trait))
                for property_, value in self.__entities[ref.toString()][trait].items():
                    self.assertEqual(result.getTraitProperty(trait, property_), value)


class Test_preflight(FixtureAugmentedTestCase):
    def test_when_refs_valid_then_are_passed_through_unchanged(self):
        entity_references = [
            self._manager.createEntityReference(s)
            for s in ["bal:///A ref to a 🐔", "bal:///anotherRef"]
        ]
        trait_set = {"a_trait", "another_trait"}
        context = self.createTestContext(access=Context.Access.kWrite)

        result_references = [None] * len(entity_references)

        self._manager.preflight(
            entity_references,
            trait_set,
            context,
            lambda idx, ref: operator.setitem(result_references, idx, ref),
            lambda _idx, _err: self.fail("Preflight should not error for this input"),
        )

        self.assertEqual(result_references, entity_references)


class Test_register(FixtureAugmentedTestCase):
    def test_when_ref_is_new_then_entity_created_with_same_reference(self):
        context = self.createTestContext()
        data = TraitsData()
        data.setTraitProperty("a_trait", "a_property", 1)
        new_entity_ref = self._manager.createEntityReference(
            "bal:///test_when_ref_is_new_then_entity_created_with_same_reference")
        published_entity_ref = self.__create_test_entity(new_entity_ref, data, context)

        context.access = Context.Access.kRead
        self.assertTrue(self._manager.entityExists([published_entity_ref], context)[0])
        self.assertEqual(published_entity_ref, new_entity_ref)

    def test_when_ref_exists_then_entity_updated_with_same_reference(self):
        context = self.createTestContext()
        data = TraitsData()
        data.setTraitProperty("a_trait", "a_property", 1)

        test_entity_ref = self._manager.createEntityReference(
            "bal:///test_when_ref_exsits_then_entity_updated_with_same_reference")
        existing_entity_ref = self.__create_test_entity(test_entity_ref, data, context)

        original_data = TraitsData(data)
        data.setTraitProperty("a_trait", "a_property", 2)

        updated_refs = [None]

        context.access = Context.Access.kWrite
        self._manager.register(
            [existing_entity_ref],
            [data],
            context,
            lambda idx, ref: operator.setitem(updated_refs, idx, ref),
            lambda _, err: self.fail(f"Register should not error: {err.code} {err.message}"),
        )

        resolved_data = [None]

        context.access = Context.Access.kRead
        self._manager.resolve(
            updated_refs,
            {"a_trait"},
            context,
            lambda idx, data: operator.setitem(resolved_data, idx, data),
            lambda _, err: self.fail(f"Resolve should not error: {err.code} {err.message}"),
        )

        self.assertEqual(resolved_data[0], data)
        self.assertNotEqual(resolved_data[0], original_data)


    def __create_test_entity(self, ref, data, context):
        """
        Creates a new entity in the library for testing.
        Asserts that the entity does not exist prior to creation.
        """
        ## @TODO (tc) Resurrect "scoped context override"?
        old_access = context.access

        context.access = Context.Access.kRead
        self.assertFalse(
            self._manager.entityExists([ref], context)[0],
            f"Entity '{ref.toString()}' already exists"
        )

        published_refs = [None]

        context.access = Context.Access.kWrite
        self._manager.register(
            [ref],
            [data],
            context,
            lambda idx, published_ref: operator.setitem(published_refs, idx, published_ref),
            lambda _, err: self.fail(f"Failed to create new entity: {err.code} {err.message}"),
        )

        context.access = old_access
        return published_refs[0]
