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
Testing that ManagerInterface methods release the GIL.
"""
# pylint: disable=redefined-outer-name,too-many-public-methods
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import access
from openassetio.managerApi import ManagerInterface, ManagerStateBase


class Test_ManagerInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    Two `ManagerInterface` instances are involved: a pure C++
    implementation (`ThreadedManagerInterface`) and a Python
    implementation (`ValidatingMockManagerInterface`). The C++
    implementation composes the Python implementation.

    The C++ implementation is called from Python in these tests. It is
    this implementation that we're testing, or rather, the Python
    binding wrapper around this implementation.

    Each method of the C++ implementation forwards its call to the
    Python implementation in a new thread, and awaits the result. The
    pybind11 trampoline will then acquire the GIL in this new thread
    (done by pybind11 as part of its trampoline macros), then call out
    to the pure Python implementation.

    Therefore, the pybind11 bindings must release the GIL on the way in
    to the C++ implementation, so that the pybind11 trampoline can
    acquire the GIL in the new thread before calling the  Python
    implementation.

    If the GIL is not released in the bindings, then we have a deadlock
    and the test will hang indefinitely. A PyGILState_Check is performed
    in the C++ implementation to preempt this and throw an exception.

    Arguably, we could get rid of the Python implementation, and instead
    have the C++ methods spawn and await a thread that simply acquires
    the GIL and returns. Forwarding to a Python implementation just
    serves to test that pybind11's trampoline is behaving as expected
    (i.e. acquires the GIL). It's also a handy way to construct dummy
    return values in the pytest test case, rather than doing that in
    the C++ implementation.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all ManagerInterface methods.
        """
        unimplemented = find_unimplemented_test_cases(ManagerInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.{method}(a_context, a_host_session)
"""
                )

        assert unimplemented == []

    def test_createChildState(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.createChildState.return_value = ManagerStateBase()

        a_threaded_mock_manager_interface.createChildState(ManagerStateBase(), a_host_session)

    def test_createState(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.createState.return_value = ManagerStateBase()
        a_threaded_mock_manager_interface.createState(a_host_session)

    def test_defaultEntityReference(
        self, a_threaded_mock_manager_interface, a_context, a_host_session
    ):
        a_threaded_mock_manager_interface.defaultEntityReference(
            [],
            access.DefaultEntityAccess.kRead,
            a_context,
            a_host_session,
            fail,
            fail,
        )

    def test_displayName(self, mock_manager_interface, a_threaded_mock_manager_interface):
        mock_manager_interface.mock.displayName.return_value = "My Name"
        assert a_threaded_mock_manager_interface.displayName() == "My Name"

    def test_entityExists(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.entityExists([], a_context, a_host_session, fail, fail)

    def test_entityTraits(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.entityTraits(
            [], access.EntityTraitsAccess.kRead, a_context, a_host_session, fail, fail
        )

    def test_flushCaches(self, a_threaded_mock_manager_interface, a_host_session):
        a_threaded_mock_manager_interface.flushCaches(a_host_session)

    def test_getWithRelationship(
        self, a_threaded_mock_manager_interface, a_traits_data, a_context, a_host_session
    ):
        a_threaded_mock_manager_interface.getWithRelationship(
            [],
            a_traits_data,
            set(),
            1,
            access.RelationsAccess.kRead,
            a_context,
            a_host_session,
            fail,
            fail,
        )

    def test_getWithRelationships(
        self, a_threaded_mock_manager_interface, an_entity_reference, a_context, a_host_session
    ):
        a_threaded_mock_manager_interface.getWithRelationships(
            an_entity_reference,
            [],
            set(),
            1,
            access.RelationsAccess.kRead,
            a_context,
            a_host_session,
            fail,
            fail,
        )

    def test_hasCapability(self, a_threaded_mock_manager_interface):
        a_threaded_mock_manager_interface.hasCapability(
            ManagerInterface.Capability.kManagementPolicyQueries
        )

    def test_identifier(self, mock_manager_interface, a_threaded_mock_manager_interface):
        mock_manager_interface.mock.identifier.return_value = ""
        a_threaded_mock_manager_interface.identifier()

    def test_info(self, a_threaded_mock_manager_interface):
        a_threaded_mock_manager_interface.info()

    def test_initialize(self, a_threaded_mock_manager_interface, a_host_session):
        a_threaded_mock_manager_interface.initialize({}, a_host_session)

    def test_isEntityReferenceString(self, a_threaded_mock_manager_interface, a_host_session):
        a_threaded_mock_manager_interface.isEntityReferenceString("", a_host_session)

    def test_managementPolicy(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.managementPolicy(
            [], access.PolicyAccess.kRead, a_context, a_host_session
        )

    def test_persistenceTokenForState(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.persistenceTokenForState.return_value = ""
        a_threaded_mock_manager_interface.persistenceTokenForState(
            ManagerStateBase(), a_host_session
        )

    def test_preflight(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.preflight(
            [], [], access.PublishingAccess.kWrite, a_context, a_host_session, fail, fail
        )

    def test_register(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.register(
            [], [], access.PublishingAccess.kWrite, a_context, a_host_session, fail, fail
        )

    def test_resolve(self, a_threaded_mock_manager_interface, a_context, a_host_session):
        a_threaded_mock_manager_interface.resolve(
            [], set(), access.ResolveAccess.kRead, a_context, a_host_session, fail, fail
        )

    def test_settings(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.settings.return_value = {}
        a_threaded_mock_manager_interface.settings(a_host_session)

    def test_stateFromPersistenceToken(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.stateFromPersistenceToken.return_value = ManagerStateBase()
        a_threaded_mock_manager_interface.stateFromPersistenceToken("", a_host_session)

    def test_updateTerminology(
        self, mock_manager_interface, a_threaded_mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.updateTerminology.return_value = {}
        a_threaded_mock_manager_interface.updateTerminology({}, a_host_session)


def fail(*_):
    pytest.fail("shouldn't have been called")
