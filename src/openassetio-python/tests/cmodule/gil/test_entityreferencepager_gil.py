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
Testing that EntityReferencePager/EntityReferencePagerInterface methods
release the GIL.
"""
# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.hostApi import EntityReferencePager
from openassetio.managerApi import EntityReferencePagerInterface


class Test_EntityReferencePagerInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `gil/Test_ManagerInterface.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(EntityReferencePagerInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_entity_ref_pager_interface, a_host_session):
        a_threaded_entity_ref_pager_interface.{method}(a_host_session)
"""
                )

        assert unimplemented == []

    def test_close(self, a_threaded_entity_ref_pager_interface, a_host_session):
        a_threaded_entity_ref_pager_interface.close(a_host_session)

    def test_get(
        self,
        mock_entity_reference_pager_interface,
        a_threaded_entity_ref_pager_interface,
        a_host_session,
    ):
        mock_entity_reference_pager_interface.mock.get.return_value = []
        a_threaded_entity_ref_pager_interface.get(a_host_session)

    def test_hasNext(
        self,
        mock_entity_reference_pager_interface,
        a_threaded_entity_ref_pager_interface,
        a_host_session,
    ):
        mock_entity_reference_pager_interface.mock.hasNext.return_value = True
        a_threaded_entity_ref_pager_interface.hasNext(a_host_session)

    def test_next(self, a_threaded_entity_ref_pager_interface, a_host_session):
        a_threaded_entity_ref_pager_interface.next(a_host_session)


class Test_EntityReferencePager_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `gil/Test_Manager.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(EntityReferencePager, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_entity_ref_pager):
        a_threaded_entity_ref_pager.{method}()
"""
                )

        assert unimplemented == []

    def test_get(self, a_threaded_entity_ref_pager, mock_entity_reference_pager_interface):
        mock_entity_reference_pager_interface.mock.get.return_value = []
        a_threaded_entity_ref_pager.get()

    def test_hasNext(self, a_threaded_entity_ref_pager, mock_entity_reference_pager_interface):
        mock_entity_reference_pager_interface.mock.hasNext.return_value = False
        a_threaded_entity_ref_pager.hasNext()

    def test_next(self, a_threaded_entity_ref_pager):
        a_threaded_entity_ref_pager.next()


@pytest.fixture
def a_threaded_entity_ref_pager(a_threaded_entity_ref_pager_interface, a_host_session):
    return EntityReferencePager(a_threaded_entity_ref_pager_interface, a_host_session)


@pytest.fixture
def a_threaded_entity_ref_pager_interface(mock_entity_reference_pager_interface):
    return _openassetio._testutils.gil.wrapInThreadedEntityReferencePagerInterface(
        mock_entity_reference_pager_interface
    )
