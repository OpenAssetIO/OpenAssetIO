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

# pylint: disable=invalid-name, missing-function-docstring

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
        context = self.createTestContext(access=Context.kRead)
        policies = self._manager.managementPolicy(self.__trait_sets, context)
        for policy in policies:
            managedTrait = ManagedTrait(policy)
            self.assertTrue(managedTrait.isValid())
            self.assertIsNone(managedTrait.getExclusive())

    def test_returns_ignored_policy_for_write_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.kWrite)
        policies = self._manager.managementPolicy(self.__trait_sets, context)
        for policy in policies:
            self.assertFalse(policy.hasTrait(ManagedTrait.kId))


class Test_managementPolicy_library_specified_behavior(FixtureAugmentedTestCase):
    """
    Tests that custom policies are loaded and respected.
    """

    __trait_sets = (
        {"definitely", "unique"},
        {"an", "ignored", "trait", "set"},
        {"a", "non", "exclusive", "trait", "set"},
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
        context = self.createTestContext(access=Context.kRead)
        expected = [TraitsData({ManagedTrait.kId}), TraitsData(), TraitsData({ManagedTrait.kId})]
        ManagedTrait(expected[0]).setExclusive(True)

        actual = self._manager.managementPolicy(self.__trait_sets, context)

        self.assertListEqual(actual, expected)

    def test_returns_ignored_policy_for_write_for_all_trait_sets(self):
        context = self.createTestContext(access=Context.kWrite)
        expected = [TraitsData(), TraitsData(), TraitsData()]

        actual = self._manager.managementPolicy(self.__trait_sets, context)

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

    def test_matches_expected_values(self):
        entity_references = self.__entities.keys()
        trait_set = {"string", "number", "test-data"}
        context = self.createTestContext(access=Context.kRead)
        results = self._manager.resolve(list(entity_references), trait_set, context)
        for ref, result in zip(entity_references, results):
            # Check all traits are present, and their properties.
            # TODO(tc): When we have a better introspection API in
            # TraitsData, we can assert there aren't any bonus values.
            for trait in self.__entities[ref].keys():
                self.assertTrue(result.hasTrait(trait))
                for property_, value in self.__entities[ref][trait].items():
                    self.assertEqual(result.getTraitProperty(trait, property_), value)
