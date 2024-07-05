#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Testing that Manager methods release the GIL.
"""
# pylint: disable=redefined-outer-name,too-many-public-methods
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import access
from openassetio.hostApi import Manager
from openassetio.managerApi import ManagerStateBase
from openassetio.trait import TraitsData


class Test_Manager_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    Two `ManagerInterface` instances are involved: a pure C++
    implementation (`ThreadedManagerInterface`) and a Python
    implementation (`ValidatingMockManagerInterface`). The C++
    implementation composes the Python implementation.

    The C++ implementation is wrapped in a Manager and called in these
    tests. It is the Manager implementation that we're testing here, or
    rather, the Python binding wrapper around it.

    See docstring for the corresponding Test_ManagerInterface for
    more details.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all ManagerInterface methods.
        """
        unimplemented = find_unimplemented_test_cases(Manager, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_manager, a_context):
        a_threaded_manager.{method}(a_context)
"""
                )

        assert unimplemented == []

    def test_contextFromPersistenceToken(
        self, mock_manager_interface, a_context, a_threaded_manager
    ):
        mock_manager_interface.mock.stateFromPersistenceToken.return_value = a_context
        a_threaded_manager.contextFromPersistenceToken("")

    def test_createChildContext(self, a_threaded_manager, a_context, a_traits_data):
        a_context.locale = a_traits_data
        a_threaded_manager.createChildContext(a_context)

    def test_createContext(self, mock_manager_interface, a_threaded_manager):
        mock_manager_interface.mock.hasCapability.return_value = True
        mock_manager_interface.mock.createState.return_value = ManagerStateBase()
        a_threaded_manager.createContext()

    def test_createEntityReference(self, a_threaded_manager):
        a_threaded_manager.createEntityReference("")

    def test_createEntityReferenceIfValid(self, a_threaded_manager):
        a_threaded_manager.createEntityReferenceIfValid("")

    def test_persistenceTokenForContext(self, a_threaded_manager, a_context):
        a_threaded_manager.persistenceTokenForContext(a_context)

    def test_defaultEntityReference(self, a_threaded_manager, a_context):
        # Defend against forgetting to include convenience signatures in
        # this test, once added.
        assert "Overloaded" not in a_threaded_manager.defaultEntityReference.__doc__

        a_threaded_manager.defaultEntityReference(
            [],
            access.DefaultEntityAccess.kRead,
            a_context,
            fail,
            fail,
        )

    def test_displayName(self, mock_manager_interface, a_threaded_manager):
        mock_manager_interface.mock.displayName.return_value = "My Name"
        assert a_threaded_manager.displayName() == "My Name"

    def test_entityExists(self, a_threaded_manager, a_context, an_entity_reference):
        ref = an_entity_reference
        tag = Manager.BatchElementErrorPolicyTag

        a_threaded_manager.entityExists([], a_context, fail, fail)
        a_threaded_manager.entityExists(ref, a_context)
        a_threaded_manager.entityExists(ref, a_context, tag.kException)
        a_threaded_manager.entityExists(ref, a_context, tag.kVariant)
        a_threaded_manager.entityExists([], a_context)
        a_threaded_manager.entityExists([], a_context, tag.kException)
        a_threaded_manager.entityExists([], a_context, tag.kVariant)

    def test_entityTraits(self, a_threaded_manager, a_context, an_entity_reference):
        ref = an_entity_reference
        an_access = access.EntityTraitsAccess.kRead
        tag = Manager.BatchElementErrorPolicyTag

        a_threaded_manager.entityTraits([], an_access, a_context, fail, fail)
        a_threaded_manager.entityTraits(ref, an_access, a_context)
        a_threaded_manager.entityTraits(ref, an_access, a_context, tag.kException)
        a_threaded_manager.entityTraits(ref, an_access, a_context, tag.kVariant)
        a_threaded_manager.entityTraits([], an_access, a_context)
        a_threaded_manager.entityTraits([], an_access, a_context, tag.kException)
        a_threaded_manager.entityTraits([], an_access, a_context, tag.kVariant)

    def test_flushCaches(self, a_threaded_manager):
        a_threaded_manager.flushCaches()

    def test_getWithRelationship(
        self, a_threaded_manager, an_entity_reference, a_traits_data, a_context
    ):
        a_threaded_manager.getWithRelationship(
            [],
            a_traits_data,
            1,
            access.RelationsAccess.kRead,
            a_context,
            fail,
            fail,
        )

        tag = Manager.BatchElementErrorPolicyTag

        a_threaded_manager.getWithRelationship(
            an_entity_reference,
            a_traits_data,
            1,
            access.RelationsAccess.kRead,
            a_context,
            set(),
            tag.kVariant,
        )

        a_threaded_manager.getWithRelationship(
            an_entity_reference,
            a_traits_data,
            1,
            access.RelationsAccess.kRead,
            a_context,
            set(),
            tag.kException,
        )

        a_threaded_manager.getWithRelationship(
            [], a_traits_data, 1, access.RelationsAccess.kRead, a_context, set(), tag.kVariant
        )

        a_threaded_manager.getWithRelationship(
            [], a_traits_data, 1, access.RelationsAccess.kRead, a_context, set(), tag.kException
        )

    def test_getWithRelationships(self, a_threaded_manager, an_entity_reference, a_context):
        a_threaded_manager.getWithRelationships(
            an_entity_reference,
            [],
            1,
            access.RelationsAccess.kRead,
            a_context,
            fail,
            fail,
        )

        tag = Manager.BatchElementErrorPolicyTag

        # No singular getWithRelationships conveniences.

        a_threaded_manager.getWithRelationships(
            an_entity_reference,
            [],
            1,
            access.RelationsAccess.kRead,
            a_context,
            set(),
            tag.kVariant,
        )

        a_threaded_manager.getWithRelationships(
            an_entity_reference,
            [],
            1,
            access.RelationsAccess.kRead,
            a_context,
            set(),
            tag.kException,
        )

    def test_hasCapability(self, a_threaded_manager):
        a_threaded_manager.hasCapability(Manager.Capability.kExistenceQueries)

    def test_identifier(self, mock_manager_interface, a_threaded_manager):
        mock_manager_interface.mock.identifier.return_value = ""
        a_threaded_manager.identifier()

    def test_info(self, a_threaded_manager):
        a_threaded_manager.info()

    def test_initialize(self, a_threaded_manager):
        a_threaded_manager.initialize({})

    def test_isEntityReferenceString(self, a_threaded_manager):
        a_threaded_manager.isEntityReferenceString("")

    def test_managementPolicy(self, mock_manager_interface, a_threaded_manager, a_context):
        mock_manager_interface.mock.managementPolicy.return_value = [TraitsData()]

        a_threaded_manager.managementPolicy(set(), access.PolicyAccess.kRead, a_context)
        a_threaded_manager.managementPolicy([], access.PolicyAccess.kRead, a_context)

    def test_preflight(self, a_threaded_manager, an_entity_reference, a_traits_data, a_context):
        an_access = access.PublishingAccess.kWrite
        tag = Manager.BatchElementErrorPolicyTag
        ref = an_entity_reference

        a_threaded_manager.preflight([], [], an_access, a_context, fail, fail)
        a_threaded_manager.preflight(ref, a_traits_data, an_access, a_context)
        a_threaded_manager.preflight(ref, a_traits_data, an_access, a_context, tag.kException)
        a_threaded_manager.preflight(ref, a_traits_data, an_access, a_context, tag.kVariant)
        a_threaded_manager.preflight([], [], an_access, a_context)
        a_threaded_manager.preflight([], [], an_access, a_context, tag.kException)
        a_threaded_manager.preflight([], [], an_access, a_context, tag.kVariant)

    def test_register(self, a_threaded_manager, an_entity_reference, a_traits_data, a_context):
        an_access = access.PublishingAccess.kWrite
        tag = Manager.BatchElementErrorPolicyTag
        ref = an_entity_reference

        a_threaded_manager.register([], [], access.PublishingAccess.kWrite, a_context, fail, fail)
        a_threaded_manager.register(ref, a_traits_data, an_access, a_context)
        a_threaded_manager.register(ref, a_traits_data, an_access, a_context, tag.kException)
        a_threaded_manager.register(ref, a_traits_data, an_access, a_context, tag.kVariant)
        a_threaded_manager.register([], [], an_access, a_context)
        a_threaded_manager.register([], [], an_access, a_context, tag.kException)
        a_threaded_manager.register([], [], an_access, a_context, tag.kVariant)

    def test_resolve(self, a_threaded_manager, an_entity_reference, a_context):
        an_access = access.ResolveAccess.kRead
        tag = Manager.BatchElementErrorPolicyTag
        ref = an_entity_reference

        # Defend against pybind11 changing its auto docs and
        # invalidating other `"Overloaded" not in` tests, above.
        assert "Overloaded" in a_threaded_manager.resolve.__doc__

        a_threaded_manager.resolve([], set(), an_access, a_context, fail, fail)
        a_threaded_manager.resolve(ref, set(), an_access, a_context)
        a_threaded_manager.resolve(ref, set(), an_access, a_context, tag.kException)
        a_threaded_manager.resolve(ref, set(), an_access, a_context, tag.kVariant)
        a_threaded_manager.resolve([], set(), an_access, a_context)
        a_threaded_manager.resolve([], set(), an_access, a_context, tag.kException)
        a_threaded_manager.resolve([], set(), an_access, a_context, tag.kVariant)

    def test_settings(self, mock_manager_interface, a_threaded_manager):
        mock_manager_interface.mock.settings.return_value = {}
        a_threaded_manager.settings()

    def test_updateTerminology(self, mock_manager_interface, a_threaded_manager):
        mock_manager_interface.mock.updateTerminology.return_value = {}
        a_threaded_manager.updateTerminology({})


def fail(*_):
    pytest.fail("shouldn't have been called")


@pytest.fixture
def a_threaded_manager(a_threaded_mock_manager_interface, a_host_session):
    return Manager(a_threaded_mock_manager_interface, a_host_session)
