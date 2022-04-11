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

from openassetio import constants, Context, SpecificationFactory
from openassetio.test.manager.harness import FixtureAugmentedTestCase


__all__ = []


class Test_managementPolicy(FixtureAugmentedTestCase):
    """
    Tests that the BAL manages all entities, for read, but nothing
    for write.
    """

    __schemas = ("file.image", "container.shot", "definitely_unique")

    def test_returns_cooperative_policy_for_read_for_all_specifications(self):
        context = self.createTestContext(access=Context.kRead)
        policies = self._manager.managementPolicy(self.__test_specs(), context)
        for policy in policies:
            self.assertEqual(policy & constants.kManaged, constants.kManaged)
            self.assertNotEqual(policy & constants.kExclusive, constants.kExclusive)

    def test_returns_ignored_policy_for_write_for_all_specifications(self):
        context = self.createTestContext(access=Context.kWrite)
        policies = self._manager.managementPolicy(self.__test_specs(), context)
        for policy in policies:
            self.assertEqual(policy, constants.kIgnored)

    @classmethod
    def __test_specs(cls):
        return [SpecificationFactory.instantiate(schema, {}) for schema in cls.__schemas]
